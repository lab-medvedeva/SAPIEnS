#!/usr/bin/env python
"""
# Author: Xiong Lei
# Created Time : Sat 28 Apr 2018 08:31:29 PM CST

# File Name: SCALE.py
# Description: Single-Cell ATAC-seq Analysis via Latent feature Extraction.
    Input: 
        scATAC-seq data
    Output:
        1. latent feature
        2. cluster assignment
        3. imputation data
"""


import time
import torch

import numpy as np
import pandas as pd
import os
import argparse

from scale import SCALE
from scale.dataset import SingleCellDataset
from scale.utils import read_labels, cluster_report, estimate_k, binarization
from scale.plot import plot_embedding

from sklearn.preprocessing import MaxAbsScaler
from torch.utils.data import DataLoader
import json
import gc
import scipy
from tensorboardX import SummaryWriter
from sklearn.metrics import adjusted_rand_score, silhouette_score


def save_binarization(recon_x, dataset, args, iteration):
    recon_x = binarization(recon_x, dataset.data).T
    imputed_dir = os.path.join(args.outdir, str(iteration))
    os.makedirs(imputed_dir, exist_ok=True)
    scipy.io.mmwrite(os.path.join(imputed_dir, 'count.mtx'), recon_x)
    pd.Series(dataset.peaks).to_csv(os.path.join(imputed_dir, 'peak.txt'), sep='\t', index=False, header=None)
    pd.Series(dataset.barcode).to_csv(os.path.join(imputed_dir, 'barcode.txt'), sep='\t', index=False, header=None)



if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='SCALE: Single-Cell ATAC-seq Analysis via Latent feature Extraction')
    parser.add_argument('--dataset', '-d', type=str, help='input dataset path')
    parser.add_argument('--n_centroids', '-k', type=int, help='cluster number')
    parser.add_argument('--outdir', '-o', type=str, default='output/', help='Output path')
    parser.add_argument('--verbose', action='store_true', help='Print loss of training process')
    parser.add_argument('--pretrain', type=str, default=None, help='Load the trained model')
    parser.add_argument('--lr', type=float, default=0.002, help='Learning rate')
    parser.add_argument('--batch_size', '-b', type=int, default=32, help='Batch size')
    parser.add_argument('--gpu', '-g', default=0, type=int, help='Select gpu device number when training')
    parser.add_argument('--seed', type=int, default=18, help='Random seed for repeat results')
    parser.add_argument('--encode_dim', type=int, nargs='*',
            #default=[1024,128],
            default=[6400, 2400, 1200, 400],
            help='encoder structure')
    parser.add_argument('--decode_dim', type=int, nargs='*', default=[], help='encoder structure')
    parser.add_argument('--latent', '-l',type=int, default=10, help='latent layer dim')
    parser.add_argument('--low', '-x', type=float, default=0.001, help='Remove low ratio peaks')
    parser.add_argument('--high', type=float, default=0.99, help='Remove high ratio peaks')
    parser.add_argument('--min_peaks', type=float, default=100, help='Remove low quality cells with few peaks')
    parser.add_argument('--log_transform', action='store_true', help='Perform log2(x+1) transform')
    parser.add_argument('--max_iter', '-i', type=int, default=30000, help='Max iteration')
    parser.add_argument('--weight_decay', type=float, default=5e-4)
    parser.add_argument('--impute', action='store_true', help='Save the imputed data')
    parser.add_argument('--binary', action='store_true', help='Save binary imputed data')
    parser.add_argument('--emb', type=str, default='UMAP')
    parser.add_argument('--reference', '-r', default=None, type=str, help='Reference celltypes')
    parser.add_argument('--transpose', '-t', action='store_true', help='Transpose the input matrix')
    parser.add_argument('--impute_iteration', type=int, default=10000, help='Impute iteration save')
    parser.add_argument('--reference_type', choices=['default', 'atlas'], help='Type of pipeline', required=True)
    parser.add_argument('--peak_save', choices=['raw', 'imputed'], help='Type of imputation', required=True)
    parser.add_argument('--experiment_name', type=str, required=True)
    args = parser.parse_args()

    experiment_path = os.path.join('summaries', args.experiment_name)

    os.makedirs('summaries', exist_ok=True)
    
    writer = SummaryWriter(experiment_path)

    # Set random seed
    seed = args.seed
    np.random.seed(seed)
    torch.manual_seed(seed)
    print(torch.cuda.is_available())
    if torch.cuda.is_available(): # cuda device
        device='cuda'
        torch.cuda.set_device(args.gpu)
    else:
        device='cpu'
    batch_size = args.batch_size

    normalizer = MaxAbsScaler()
    dataset = SingleCellDataset(args.dataset, low=args.low, high=args.high, min_peaks=args.min_peaks,
                                transpose=args.transpose, transforms=[normalizer.fit_transform])
    trainloader = DataLoader(dataset, batch_size=batch_size, shuffle=True, drop_last=True)
    testloader = DataLoader(dataset, batch_size=batch_size, shuffle=False, drop_last=False)

    cell_num = dataset.shape[0] 
    input_dim = dataset.shape[1] 	
    
    if args.n_centroids is None:
        k = min(estimate_k(dataset.data.T), 30)
        print('Estimate k {}'.format(k))
    else:
        k = args.n_centroids
    lr = args.lr
    name = args.dataset.strip('/').split('/')[-1]
    args.min_peaks = int(args.min_peaks) if args.min_peaks >= 1 else args.min_peaks
    
    outdir = args.outdir
    if not os.path.exists(outdir):
        os.makedirs(outdir)
        
    print("\n**********************************************************************")
    print("  SCALE: Single-Cell ATAC-seq Analysis via Latent feature Extraction")
    print("**********************************************************************\n")
    print("======== Parameters ========")
    print('Cell number: {}\nPeak number: {}\nn_centroids: {}\nmax_iter: {}\nbatch_size: {}\ncell filter by peaks: {}\nrare peak filter: {}\ncommon peak filter: {}'.format(
        cell_num, input_dim, k, args.max_iter, batch_size, args.min_peaks, args.low, args.high))
    print("============================")

    dims = [input_dim, args.latent, args.encode_dim, args.decode_dim]
    model = SCALE(dims, n_centroids=k)
#     print(model)

    if not args.pretrain:
        print('\n## Training Model ##')
        model.init_gmm_params(testloader)
        if args.reference_type == 'default':
            ref_cells = pd.read_csv(args.reference, sep=',', index_col='cell_id')['cell_types']
        else:
            ref = pd.read_csv(args.reference, sep='\t', header=None, index_col=0)
            ref_cells = ref[1]
            ref_peaks = ref.index
        print(dataset.barcode)
        print(ref_cells)
        labels = ref_cells.reindex(dataset.barcode, fill_value='unknown')
        cell_types = ref_cells.unique()
        for iteration in model.fit(trainloader,
                  lr=lr, 
                  weight_decay=args.weight_decay,
                  verbose=args.verbose,
                  device = device,
                  max_iter=args.max_iter,
                  name=name,
                  outdir=outdir
                  ):
            feature = model.encodeBatch(testloader, device=device, out='z')
            # labels_filtered = labels[labels != 'Unknown']
            # feature_filtered = feature[labels != 'Unknown']
            try:
                embedding = plot_embedding(
                    feature, labels,
                    method=args.emb, 
                    save=os.path.join(outdir, f'emb_{args.emb}_{iteration}.pdf'),
                    save_emb=os.path.join(outdir, f'emb_{args.emb}_{iteration}.txt'),
                    return_emb=True
                )
            except ValueError:
                print('Value contains NaNs')

			 
            if (iteration + 1) % args.impute_iteration == 0:
                recon_x = model.encodeBatch(testloader, device, out='x', transforms=[normalizer.inverse_transform])
                save_binarization(recon_x, dataset, args, iteration + 1)
                imputed_data = recon_x.T
                print(dataset.data.T.shape, imputed_data.shape, 'dataset shape')
                if args.peak_save == 'imputed':
                    first_condition = (imputed_data.T > imputed_data.mean(axis=1)).T
                    second_condition = imputed_data > imputed_data.mean(axis=0)
                else:
                    first_condition = (imputed_data.T > dataset.data.mean(axis=1)).T
                    second_condition = (imputed_data > dataset.data.mean(axis=0).T)
                
                binary_imputed_data = first_condition & second_condition

                stats_info = {
                    'num_non_empty': int(np.sum(binary_imputed_data)),
                    'num_cells': int(np.prod(binary_imputed_data.shape))
                }
                print(iteration, np.sum(binary_imputed_data), np.prod(binary_imputed_data.shape))
                del first_condition
                del second_condition
                recon_x = pd.DataFrame(binary_imputed_data, index=dataset.peaks, columns=dataset.barcode)

                del binary_imputed_data

                gc.collect()

                pred = model.predict(testloader, device)

                ari = adjusted_rand_score(labels, pred)

                # silhouette = silhouette_score(labels, pred)

                writer.add_scalar('metrics/ari', ari, iteration + 1)
                # writer.add_scalar('metrics/silhouette', silhouette_score, iteration + 1)
                print('ARI', adjusted_rand_score(labels, pred))
                # print('Silhouette', silhouette_score(labels, pred))


                cluster_predictions = pd.Series(pred, index=dataset.barcode)

                silhouette = silhouette_score(embedding, labels)

                writer.add_scalar('metrics/silhouette', silhouette, iteration + 1)
                writer.flush()

                for index in range(k):
                    type_specific_cells = list(labels[cluster_predictions == index].index)
                    cell_type_matrix = recon_x[type_specific_cells]

                    sum_by_peaks = cell_type_matrix.sum(axis=1) >= 1
                    del cell_type_matrix
                    gc.collect()
                    filtered_peaks = sum_by_peaks[sum_by_peaks >= 1]

                    filtered_peaks.to_csv(
                        os.path.join(outdir, f'imputed_data_{args.peak_save}_{iteration}_cluster_{index}.txt'),
                        header=None,
                        columns=[]
                    )


                for cell_type in cell_types:
                    type_specific_cells = list(labels[labels == cell_type].index)
                    
                    cell_type_matrix = recon_x[type_specific_cells]

                    sum_by_peaks = cell_type_matrix.sum(axis=1) >= 1
                    del cell_type_matrix
                    gc.collect()
                    filtered_peaks = sum_by_peaks[sum_by_peaks >= 1]
                    stats_info[f'{cell_type}_peaks'] = len(filtered_peaks)
                    print(iteration, cell_type, len(filtered_peaks))
                    filtered_peaks.to_csv(
                        os.path.join(outdir, f'imputed_data_{args.peak_save}_{iteration}_{cell_type.replace(" ", "_").replace("/", "_")}.txt'),
                        header=None,
                        columns=[]
                    )
                with open(os.path.join(outdir, f'stats_{args.peak_save}_{iteration}.json'), 'w') as fp:
                    json.dump(stats_info, fp)

                cluster_predictions.to_csv(os.path.join(outdir, f'cluster_assignments_{iteration}.txt'), sep='\t', header=False)
     
            gc.collect()  
#         torch.save(model.to('cpu').state_dict(), os.path.join(outdir, 'model.pt')) # save model
    else:
        print('\n## Loading Model: {}\n'.format(args.pretrain))
        model.load_model(args.pretrain)
        model.to(device)

    ### output ###
    print('outdir: {}'.format(outdir))
    # 1. latent feature
    feature = model.encodeBatch(testloader, device=device, out='z')
    pd.DataFrame(feature).to_csv(os.path.join(outdir, 'feature.txt'), sep='\t', header=False)

    # 2. cluster assignments
    pred = model.predict(testloader, device)
    pd.Series(pred, index=dataset.barcode).to_csv(os.path.join(outdir, 'cluster_assignments.txt'), sep='\t', header=False)
            
    # 3. imputed data
    if args.impute or args.binary:
        recon_x = model.encodeBatch(testloader, device, out='x', transforms=[normalizer.inverse_transform])
        if args.binary:
            import scipy
            print("Saving binary imputed data")
            recon_x = binarization(recon_x, dataset.data).T
            imputed_dir = outdir+'/binary_imputed/'
            os.makedirs(imputed_dir, exist_ok=True)
            scipy.io.mmwrite(imputed_dir+'count.mtx', recon_x)
            pd.Series(dataset.peaks).to_csv(imputed_dir+'peak.txt', sep='\t', index=False, header=None)
            pd.Series(dataset.barcode).to_csv(imputed_dir+'barcode.txt', sep='\t', index=False, header=None)
        elif args.impute:
            print("Saving imputed data")
            imputed_data = recon_x.T
            binary_imputed_data = ((imputed_data.T > imputed_data.mean(axis=1)).T & imputed_data > imputed_data.mean(axis=0)).astype(int)
            recon_x = pd.DataFrame(binary_imputed_data, index=dataset.peaks, columns=dataset.barcode)
            recon_x.to_csv(os.path.join(outdir, 'imputed_data.txt'), sep='\t') 

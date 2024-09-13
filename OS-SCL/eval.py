import sys
import torch
from torch.utils.data import DataLoader
from sklearn import metrics
from model.net import SCLTFSTgramMFN
from losses import ASDLoss
from dataloader import test_dataset
import yaml
from tqdm import tqdm
import argparse


def load_config(file_path):
    with open(file_path, 'r', encoding='UTF-8') as f:
        return yaml.load(f, Loader=yaml.FullLoader)


def save_config(cfg, file_path):
    with open(file_path, 'w', encoding='UTF-8') as f:
        yaml.dump(cfg, f)


def update_config(cfg, args):
    for key, value in vars(args).items():
        if value is not None:
            cfg[key] = value
    return cfg


def parse_arguments():
    parser = argparse.ArgumentParser(description='Modify YAML configuration.')
    parser.add_argument('--alpha', type=float, help='Alpha value')
    parser.add_argument('--m', type=float, help='m value')
    parser.add_argument('--gpu_num', type=int, help='GPU number')
    parser.add_argument('--epoch', type=int, help='Number of epochs')
    parser.add_argument('--num_classes', type=int, help='Number of classes')
    parser.add_argument('--split_ratio', type=float, help='Split ratio')
    parser.add_argument('--batch_size', type=int, help='Batch size')
    parser.add_argument('--lr', type=float, help='Learning rate')
    parser.add_argument('--mode', type=str, help='Mode')
    parser.add_argument('--margin', type=str, help='Margin')
    parser.add_argument('--local', type=bool, help='Local')
    parser.add_argument('--load_memory', type=bool, help='Load memory')
    parser.add_argument('--fussion', type=int, help='Fussion')
    parser.add_argument('--conv', action='store_true', help='conv or linear')
    parser.add_argument('--ht', type=str, help='Action function')
    parser.add_argument('--d', action='store_true', help='Use development dataset for evaluation.')
    parser.add_argument('--e', action='store_true', help='Use evaluation dataset for evaluation.')
    return parser.parse_args()


def evaluator(net, test_loader, criterion, device, machine, cfg):
    net.eval()

    y_truet = []
    y_predt = []
    id_auc_pauc = {}
    progress_bar = tqdm(test_loader, desc=f'{machine} evaling', leave=False, dynamic_ncols=True)
    with torch.no_grad():
        for x_wavs, x_mels, labels, AN_N_labels, id_label in progress_bar:
            x_wavs, x_mels, labels, AN_N_labels = x_wavs.to(device), x_mels.to(device), labels.to(
                device), AN_N_labels.to(device)
            id_label = ''.join(id_label)

            logits, _ = net(x_wavs, x_mels, labels, train=False)

            score = criterion(logits, labels)
            y_predt.extend(score.tolist())

            y_truet.extend(AN_N_labels.tolist())
            if id_label not in id_auc_pauc:
                id_auc_pauc[id_label] = {'y_true': [], 'y_pred': []}
            id_auc_pauc[id_label]['y_true'].extend(AN_N_labels.tolist())
            id_auc_pauc[id_label]['y_pred'].extend(score.tolist())

    id_results = {}
    for id_label, data in id_auc_pauc.items():
        y_true = data['y_true']
        y_pred = data['y_pred']
        auc = metrics.roc_auc_score(y_true, y_pred)
        pauc = metrics.roc_auc_score(y_true, y_pred, max_fpr=0.1)
        id_results[id_label] = (auc, pauc)

    min_id = min(id_results, key=lambda k: id_results[k][0])
    min_auc = id_results[min_id][0]

    auc = metrics.roc_auc_score(y_truet, y_predt)
    pauc = metrics.roc_auc_score(y_truet, y_predt, max_fpr=0.1)

    # 打印最低AUC的ID
    print("=" * 40)
    print(f"Machine: {machine}")
    print(f"Minimum ID: {min_id}, Minimum AUC: {min_auc:.4f}")
    print(f"AUC: {auc:.4f}, pAUC: {pauc:.4f}")

    return auc, pauc, min_auc


def main():
    args = parse_arguments()
    cfg = load_config('config.yaml')
    print('Original Configuration...')
    print(cfg)

    cfg = update_config(cfg, args)
    print('Updated Configuration...')
    print(cfg)

    device_num = cfg['gpu_num']

    device = torch.device(f'cuda:{device_num}')

    net = SCLTFSTgramMFN(num_classes=cfg['num_classes'], mode=cfg['mode'], margin=cfg['margin'], m=cfg['m'],
                         nsc=cfg['n_subclusters'], cfg=cfg).to(device)

    net.load_state_dict(
        torch.load(
            'xx.pth',
            map_location=device))
    net.eval()

    if cfg["fussion"] == 4 or cfg["fussion"] == 5:
        criterion = ASDLoss().to(device)
    else:

        criterion = ASDLoss(reduction=False).to(device)

    data_loaders = {}
    name_list = ['fan', 'pump', 'slider', 'ToyCar', 'ToyConveyor', 'valve']

    if args.d:
        root_path = '../data/dataset'
        print("Using development dataset for evaluation.")
    elif args.e:
        root_path = '../data/eval_dataset'
        print("Using evaluation dataset for evaluation.")
    else:
        print("Error: You must provide either --d for development or --e for evaluation.")
        sys.exit(1)

    avg_AUC = 0.
    avg_pAUC = 0.
    mini_auc = 0.
    for machine_type in name_list:
        test_ds = test_dataset(root_path, machine_type, name_list, cfg)
        test_dataloader = DataLoader(test_ds, batch_size=1, pin_memory=True, num_workers=8)
        data_loaders[machine_type] = test_dataloader

    for machine_type, test_dataloader in data_loaders.items():
        AUC, PAUC, mauc = evaluator(net, test_dataloader, criterion, device, machine_type, cfg)
        avg_AUC += AUC
        avg_pAUC += PAUC
        mini_auc += mauc
        # print(f"{machine_type} - AUC: {AUC:.5f}, pAUC: {PAUC:.5f}")

    avg_AUC /= len(name_list)
    avg_pAUC /= len(name_list)
    mini_auc /= len(name_list)
    print(f"Average AUC: {avg_AUC:.5f},  Average pAUC: {avg_pAUC:.5f} ,Average mAUC: {mini_auc:.5f}")


if __name__ == '__main__':
    main()

import pickle
import numpy as np
import torch

def clean_pkl():
    subject_ids = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 13, 14, 15, 16, 17]
    freqs = {'chest': {sensor: 700 for sensor in {'ACC', 'ECG', 'EMG', 'EDA', 'Temp', 'Resp'}},
            'wrist': {'ACC': 32, 'BVP': 64, 'EDA': 4, 'TEMP': 4}}
    for id in subject_ids:
        print(end=f'Doing S{id}')
        with open(f"WESAD/S{id}/S{id}.pkl", 'rb') as file:
            data = pickle.load(file, encoding='bytes')
        labels:np.ndarray = data[b'label']
        signals = data[b'signal']
        labels_sec = labels.reshape((-1, 700 // 4))
        tmp_data = {device: 
                    {sensor.decode(): 
                        signals[device.encode()][sensor].reshape((-1, 3 if sensor == b'ACC' else 1, freqs[device][sensor.decode()] // 4))
                        for sensor in signals[device.encode()]} 
                    for device in ['wrist', 'chest']}
        goods = (labels_sec.min(axis=1) > 0) & (labels_sec.max(axis=1) < 5)
        labels_sec_good = labels_sec[goods]
        end_data:dict[str, torch.Tensor] = {f"{device}_{sensor}": torch.tensor(tmp_data[device][sensor][goods]) for device in tmp_data for sensor in tmp_data[device]}
        end_data['label'] = torch.tensor(labels_sec_good)
        print(end=f'\rWriting S{id}')
        with open(f"WESAD/S{id}/S{id}_n0.pkl", 'wb') as file:
            pickle.dump(end_data, file)
        print(f'\rS{id} Finished ({labels.shape} -> {end_data["label"].shape} seconds)')
    
clean_pkl()

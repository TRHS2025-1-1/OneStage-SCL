# OneStage-SCL

Thank you for visiting this repository! The code is currently being meticulously organized and refined to ensure the highest quality and usability. I am fully committed to making it publicly available very soon.

## Project Overview
This repository will soon host the implementation of an innovative approach for anomalous sound detection. 

## 1. Dataset Preparation

To get started with this project, follow the steps below to prepare the dataset:

### Step 1: Download the Dataset
First, you need to download all the necessary files. This can be done by running the script located in the `1.Preparation` folder:

```bash
bash dataset_download.sh
```

### Step 2: Rename Evaluation Set Files
After downloading the dataset, move all the files from the `Rename_Evaluation_set` folder to the evaluation dataset directory:

```bash
mv Rename_Evaluation_set/* /path/to/evaluation_dataset_directory/
```

Make sure to replace `/path/to/evaluation_dataset_directory/` with the actual path where your evaluation dataset is stored.

Your evaluation dataset directory should have the following structure after this step:

```bash
/path/to/evaluation_dataset_directory/
│
├── fan/
│   ├── test/
│   ├── train/
│
├── valve/
│   ├── test/
│   ├── train/ 
│
├── slider/
│   ├── test/
│   ├── train/
│
├── pump/
│   ├── test/
│   ├── train/
│
├── Toycar/
│   ├── test/
│   ├── train/
│
├── Toyconveyor/
│   ├── test/
│   ├── train/
│
├── fan.csv
├── valve.csv
├── slider.csv
├── pump.csv
├── toycar.csv
├── toyconveyor.csv
└── split.py
```

### Step 3: Split the Dataset
Finally, to prepare the dataset for training and evaluation, run the `split.py` script:

```bash
python split.py
```

This will organize the dataset into the necessary structure for the subsequent stages of the project.

## 2. Model Training and OS-SCL Framework

With the dataset prepared, the next step is to train the model using the OneStage-SCL (OS-SCL) framework. This section provides an overview of the core training process.


### Training the Model
The core training code is now available, allowing you to start training the model using the OS-SCL framework. However, please note that the complete training code, including all details and configurations, will be made publicly available very soon.


### Upcoming Release
I am currently finalizing the full training code, which includes all hyperparameters, model configurations, and detailed documentation. This will be released shortly, so please stay tuned for updates!

## Contact Information
If you have any questions, suggestions, or would like to discuss potential collaborations, please don’t hesitate to reach out to me:

- **Email**: [huangswt@stu.xju.edu.cn](mailto:huangswt@stu.xju.edu.cn)
- **WeChat**: TwoIcp12

I sincerely appreciate your interest and eagerly look forward to sharing the full project with you in the near future. Your patience and support mean a lot!


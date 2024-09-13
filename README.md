Here's how you can modify your repository's README to include a clear and structured dataset preparation section:

---

# OneStage-SCL

Thank you for visiting this repository! The code is currently being meticulously organized and refined to ensure the highest quality and usability. I am fully committed to making it publicly available very soon.

## Project Overview
This repository will soon host the implementation of an innovative approach for anomalous sound detection. The method is designed to push the boundaries of current technology, and I am excited to share it with the community. Stay tuned for updates!

## 1. Dataset Preparation

To get started with this project, follow the steps below to prepare the dataset:

### Step 1: Download the Dataset
First, you need to download all the necessary files. This can be done by running the script located in the `1.Preparation` folder:

```bash
cd 1.Preparation
bash dataset_download.sh
```

### Step 2: Rename Evaluation Set Files
After downloading the dataset, move all the files from the `Rename_Evaluation_set` folder to the evaluation dataset directory:

```bash
mv Rename_Evaluation_set/* /path/to/evaluation_dataset_directory/
```

Make sure to replace `/path/to/evaluation_dataset_directory/` with the actual path where your evaluation dataset is stored.

### Step 3: Split the Dataset
Finally, to prepare the dataset for training and evaluation, run the `split.py` script:

```bash
python split.py
```

This will organize the dataset into the necessary structure for the subsequent stages of the project.

## Contact Information
If you have any questions, suggestions, or would like to discuss potential collaborations, please don’t hesitate to reach out to me:

- **Email**: [huangswt@stu.xju.edu.cn](mailto:huangswt@stu.xju.edu.cn)
- **WeChat**: TwoIcp12

I sincerely appreciate your interest and eagerly look forward to sharing the full project with you in the near future. Your patience and support mean a lot!

---

This section should guide users through the dataset preparation process clearly and efficiently. Let me know if you need further adjustments!

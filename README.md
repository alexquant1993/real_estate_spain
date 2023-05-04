# Step 1: Create a new project in Google Cloud Platform
- Create a Google Cloud Platform account
- Create a new project: idealista-scraper. ID = idealista-scraper-384619
- Enable Compute Engine API

# Step 2: Install Google Cloud SDK
- Install Google Cloud SDK from https://cloud.google.com/sdk/docs/install#windows
    - On Windows use chocolatey, make sure you run CMD on admin mode: `choco install google-cloud-sdk`
    - To update: `choco upgrade google-cloud-sdk`
- Check installation with `gcloud version`. Output:
```bash
Google Cloud SDK 427.0.0
bq 2.0.91
core 2023.04.17
gcloud-crc32c 1.0.0
gsutil 5.23
```

# Step 3: Configure permissions with Google Cloud CLI
Create an IAM service account to enable Terraform access to Google Cloud Platform.
- Login to Google Cloud Platform with `gcloud auth login`
- Update GCP: `gcloud components update`
- Create a variable with the project ID:`PROJECT_ID="idealista-scraper-384619"`
- Set to project `gcloud config set project $PROJECT_ID`
- Create a service account: `gcloud iam service-accounts create terraform-iam --display-name "terraform-iam"`
- Check service account: `gcloud iam service-accounts list`
- Define roles:

```bash
# This role provides full access to resources within the project, including the ability to create and delete resources.
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:terraform-iam@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/editor"
# This role provides full access to Google Cloud Storage resources within the project, including the ability to create and delete buckets and objects.
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:terraform-iam@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/storage.admin"
# This role provides full access to objects within Google Cloud Storage buckets within the project, including the ability to create and delete objects.
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:terraform-iam@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/storage.objectAdmin"
# This role provides full access to BigQuery resources within the project, including the ability to create and delete datasets and tables.
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:terraform-iam@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/bigquery.admin"
```
- Create directory to store credentials: `mkdir ~/.gcp`
- Download JSON credentials: `gcloud iam service-accounts keys create ~/.gcp/terraform.json --iam-account=terraform-iam@$PROJECT_ID.iam.gserviceaccount.com`
- Login with service account: `gcloud auth activate-service-account --key-file ~/.gcp/terraform.json`

# Step 4: Install Terraform
Terraform is a tool for infrastructure as code, allowing you to define and manage your infrastructure in a declarative manner. With Terraform, you can provision and manage infrastructure across multiple providers and environments, making it easier to maintain consistency and reduce errors. Terraform also provides a way to version and track changes to your infrastructure, making it easier to collaborate and audit changes over time.

- Install Terraform: https://www.terraform.io/downloads.html
    - On Windows use chocolatey, make sure you run CMD on admin mode: `choco install terraform`
    - To update: `choco upgrade terraform`
- Check that Terraform is installed: `terraform version`. Output:
```bash
Terraform v1.4.5
on windows_amd64
```

# Step 5: Create GCP resources with Terraform
- Create terraform directory: `mkdir terraform`
- Move to terraform directory: `cd terraform`
- Create a file named `main.tf` where we will define the resources we want to create in GCP.
    - Create a VM instance: e2-medium (2 vCPUs, 4 GB memory), Ubuntu 20.04 LTS, 20 GB disk. A ssh key pair will be used to connect to the VM.
    - Create a GCS bucket
    - Create a BigQuery dataset
- Create a file named `variables.tf` where we will define the variables we will use in `main.tf`.
    - Establish the project ID
    - Establish the region and zone
    - Establish VM details: machine type, image, disk size
    - Establish GCS bucket name and storage class
    - Establish BigQuery dataset name
- Initialize Terraform: `terraform init`
- Terraform validate: `terraform validate`
- Terraform plan: `terraform plan -var "credentials=~/.gcp/terraform.json" -var "vm_ssh_user=aarroyo" -var "vm_ssh_pub_key=~/.ssh/idealista_vm.pub" -out=tfplan`
    - Enter DigitalOcean token - DO is used given that offers cheaper VMs than GCP. The token can be obtained from the DO dashboard.
    - Enter GCP credentials JSON file path: `~/.gcp/terraform.json`
    - Enter path to the SSH public key for VM: `~/.ssh/idealista_vm.pub`
        - Previously generate a SSH key pair: `ssh-keygen`
        - Select a file name to save the key pair: `~/.ssh/idealista_vm`
    - Enter SSH username for VM: `aarroyo`
- Terraform apply: `terraform apply "tfplan"`
- Check that the resources have been created in GCP dashboard.
- If you want to destroy the resources created with Terraform: `terraform destroy -var "credentials=~/.gcp/terraform.json" -var "vm_ssh_user=aarroyo" -var "vm_ssh_pub_key=~/.ssh/idealista_vm.pub"`

# Step 6: Connect to VM instance
- Install Remote SSH extension in VSCode
- Check the VM instance IP address: `gcloud compute instances list`
- Edit the config file in `~/.ssh/config` to add the VM instance:
```bash
Host idealista_vm
	Hostname {vm_ip_address}
	User root
    Port 22
	IdentityFile {~/.ssh/private_ssh_key}
```
- Connect to VM instance using the Remote SSH extension in VSCode. Select remote and then connect in new window.
- This will open a new VSCode window with the VM instance connected.
- Create a new user in the VM instance: `sudo adduser aarroyo && sudo usermod -aG sudo aarroyo`
- Change user to `aarroyo`: `sudo su - aarroyo`

# Step 7: Install packages and software in VM instance
- Check CPU and disk space information: `lscpu` and `df -h`
- Install and update packages:
```bash
sudo apt-get update
sudo apt-get upgrade -y
sudo apt-get install bzip2 libxml2-dev
# Install the required language pack
sudo apt-get install language-pack-es-base
```
- Install Anaconda:
```bash
wget https://repo.anaconda.com/archive/Anaconda3-2023.03-1-Linux-x86_64.sh -O ~/anaconda.sh
bash ~/anaconda.sh -b -p $HOME/anaconda3
echo 'export PATH="$HOME/anaconda3/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
rm -f ~/anaconda.sh
```
> To fix the SSH warning after destroying and recreating a VM instance with Terraform, remove the old key fingerprint from the known_hosts file and try to connect again to the VM.

- Install and setup Git:
    - Install git: `sudo apt-get install git`
    - Configure git: `git config --global user.name "Your Name"` and `git config --global user.email youremail@example.com`
- Generate a SSH key: `ssh-keygen -t rsa -b 4096 -C "youremail@example.com"`
- Add the SSH key to your GitHub account: 
    - Copy the public SSH key: `cat ~/.ssh/id_rsa.pub`
    - Go to GitHub settings > SSH and GPG keys > New SSH key
    - Paste the public SSH key and save
    - Test the SSH connection: `ssh -T git@github.com`
- Clone the repository: `git clone git@github.com:alexquant1993/real_estate_spain.git`
- Create a conda environment and install the neccesary packages:
```bash
conda create -n re-spain python=3.11
conda init bash
# Close and reopen your terminal
conda activate re-spain
cd real_estate_spain
pip install -r requirements.txt
```

## Prefect setup
1. Run prefect as a (systemd service)[https://docs.prefect.io/orchestration/tutorial/overview.html#running-prefect-as-a-systemd-service].
    - Create a new systemd service unit file in the /etc/systemd/system/ directory: `sudo nano /etc/systemd/system/prefect-agent.service`
    - Copy and paste the following configuration into the service file:
    ```bash
    [Unit]
    Description=Prefect Agent

    [Service]
    Type=simple
    User=aarroyo
    WorkingDirectory=/home/aarroyo/real_estate_spain
    ExecStart=/home/aarroyo/anaconda3/envs/re-spain/bin/prefect agent start -q default
    Restart=always

    [Install]
    WantedBy=multi-user.target
    ```
    - Reload the systemd daemon to read the new service configuration: `sudo systemctl daemon-reload`
    - Enable the service to ensure that it starts on boot: `sudo systemctl enable prefect-agent`
    - Start the prefect service: `sudo systemctl start prefect-agent`
    - Check the status of the service: `sudo systemctl status prefect-agent`
    - Check that everything is working properly: `systemctl --type=service | grep prefect`

> If the agent is not picking up the flow runs you can do: `sudo systemctl daemon-reload && sudo systemctl restart prefect-agent && sudo systemctl status prefect-agent`

2. Repeat steps in section 3 in order to connect to Google Cloud with a service account:
    - In a Digital Ocean Droplet, you have to install the Google Cloud SDK: `sudo snap install google-cloud-sdk --classic`
    - Login to Google Cloud Platform with `gcloud auth login`
    - Export project ID value: `export PROJECT_ID="idealista-scraper-384619"`
    - Set project: `gcloud config set project $PROJECT_ID`
    - Create a service account: `gcloud iam service-accounts create prefect-agent --display-name "Prefect Agent"`
    - Add GCS and Bigquery roles to the service account:
        - GCS: 
            - `gcloud projects add-iam-policy-binding $PROJECT_ID --member serviceAccount:prefect-agent@$PROJECT_ID.iam.gserviceaccount.com --role roles/storage.admin`
            - `gcloud projects add-iam-policy-binding $PROJECT_ID --member serviceAccount:prefect-agent@$PROJECT_ID.iam.gserviceaccount.com --role roles/storage.objectAdmin`
        - Bigquery: `gcloud projects add-iam-policy-binding $PROJECT_ID --member serviceAccount:prefect-agent@$PROJECT_ID.iam.gserviceaccount.com --role roles/bigquery.admin`
    - Download JSON credentials: `gcloud iam service-accounts keys create ~/.gcp/prefect-agent.json --iam-account=prefect-agent@$PROJECT_ID.iam.gserviceaccount.com`
    - Login with service account: `gcloud auth activate-service-account --key-file ~/.gcp/prefect-agent.json`

# Step 8: Run the pipelines
- Login to prefect cloud: `prefect cloud login -k {YOUR_API_KEY}`
- Create deployment file: `prefect deployment build idealista_pipeline.py:idealista_to_gcp_pipeline -n madrid_sale_daily -o idealista-pipeline-daily.yaml`
- Deployment file customization:
    - Set up parameters according to your needs:
        - testing: true
        - province: madrid
        - bucket_name: idealista_data_lake_idealista-scraper-384619
        - time_period: 24
        - type_search: sale
        - credentials_path: ~/.gcp/prefect-agent.json
    - Set up the schedule:
        - cron: 0 22 * * *
        - timezone: Europe/Madrid
        - day_or: true
- Apply deployment: `prefect deployment apply idealista_to_gcs_pipeline-daily.yaml`
- Run flow: `prefect deployment run "idealista-to-gcs-pipeline/madrid_sale_daily"`
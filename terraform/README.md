# NGFF Benchmarking setup with Terraform

## Setup
* First, you will need to create an aws account. In this account, you will need an IAM user created with CLI access and admin privileges. These will be the credentials terraform will use to create resources on your behalf. You will want these credentials in the `~/.aws/credentials` file. You can set them as the default or create a terraform aws profile for them (see https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-profiles.html). 
* The next thing you'll need to do is create a bucket for terraform to store `.tfstate` files in. These are files terraform uses to keep track of the state of your infrastructure, so that it can add, modify, and destroy compenents correclty. You can keep these files on your local machine, but then there will be issues if other users want to use terraform to modify your setup. You can name this bucket anything you like. 
* In order to SSH into your instances, you'll need an RSA key pair. Generate one with a command like `ssh-keygen -l -f .ssh/aws.pem` (see Option 2 in https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-key-pairs.html for details). 
* Install terraform https://learn.hashicorp.com/tutorials/terraform/install-cli

## Run
* Clone this repo and `cd` into the `terraform` directory.
* Rename the files `tfbackend.config.example` and `terraform.tfvars.example` to remove the `.example` and edit them to have the correct values for your needs. The `bucket` in `tfbackend.config` should be the name of the bucket where you plan to store `.tfstate` files. In `terraform.tfvars`, `ssh_client_ip` should be the IP address you intend to SSH into your ec2 instances from, or `0.0.0.0/0` if you want to be able to SSH in from anywhere. `ssh_public_key` should be the public key of the `.pem` file you generated earlier. 
* Initialize terraform by running `terraform init`.
* Run `terraform plan` to make show you everything that will be created and confirm that this is correct.
* Run `terraform apply`

After this, the resources should be available (you can double-check in the aws console) and you should be able to SSH into your new hosts by looking up the DNS (either in the console or by running `terraform output`) and running `ssh -i <your-private-key>.pem ubuntu@<your-public-dns>`

## Tear Down
To remove the resources you created here, just run `terraform destroy`

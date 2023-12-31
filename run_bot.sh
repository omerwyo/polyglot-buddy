#!/bin/bash

#################################################
## TEMPLATE VERSION 1.01                       ##
#################################################
## ALL SBATCH COMMANDS WILL START WITH #SBATCH ##
## DO NOT REMOVE THE # SYMBOL                  ## 
#################################################

#SBATCH --nodes=1                   # How many nodes required? Usually 1
#SBATCH --cpus-per-task=4           # Number of CPU to request for the job
#SBATCH --mem=16GB                  # How much memory does your job require?
#SBATCH --gres=gpu:1                # Do you require GPUS? If not delete this line
#SBATCH --time=01-00:00:00          # How long to run the job for? Jobs exceed this time will be terminated
                                    # Format <DD-HH:MM:SS> eg. 5 days 05-00:00:00
                                    # Format <DD-HH:MM:SS> eg. 24 hours 1-00:00:00 or 24:00:00
#SBATCH --mail-type=BEGIN,END,FAIL  # When should you receive an email?
#SBATCH --output=%u.%j.out          # Where should the log files go?
                                    # You must provide an absolute path eg /common/home/module/username/
                                    # If no paths are provided, the output file will be placed in your current working directory

################################################################
## EDIT AFTER THIS LINE IF YOU ARE OKAY WITH DEFAULT SETTINGS ##
################################################################

#SBATCH --partition=project                 # The partition you've been assigned
#SBATCH --account=cs425   # The account you've been assigned (normally student)
#SBATCH --qos=cs425qos       # What is the QOS assigned to you? Check with myinfo command
#SBATCH --job-name=telebot     # Give the job a name

#################################################
##            END OF SBATCH COMMANDS           ##
#################################################

# Purge the environment, load the modules we require.
# Refer to https://violet.smu.edu.sg/origami/module/ for more information
module purge
module load Python/3.9.13

# Create a virtual environment
# python3 -m venv ~/myenv

# Start Ollama web server for getting inferences
( /common/home/projectgrps/CS425/CS425G6/ollama serve > /dev/null 2>&1 & )

sleep 1

# Send out a curl request to curb cold start for Llama, dont print the output
curl -X POST http://localhost:11434/api/generate -d '{"model": "vicuna", "prompt": "Why is the sky blue?"}' > /dev/null 2>&1 &

# This command assumes that you've already created the environment previously
# We're using an absolute path here. You may use a relative path, as long as SRUN is execute in the same working directory
source ~/venv/bin/activate

# srun whichgpu

# If you require any packages, install it as usual before the srun job submission.
# pip3 install numpy

# Submit your job to the cluster
# Modify this path as necessary
srun --gres=gpu:1 python -u /common/home/projectgrps/CS425/CS425G6/polyglot-buddy/telebot.py
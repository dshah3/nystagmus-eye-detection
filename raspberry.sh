# source .env

# USERNAME=$RASPBERRY_PI_USERNAME
# HOSTS=$RASPBERRY_PI_IP_ADDR
# SCRIPT = f"pwd; source {$RASPBERRY_PI_LOCAL_ENV}/bin/activate; sudo {$RASPBERRY_PI_LOCAL_ENV}/bin/python {$RASPBERRY_PI_SCRIPT_LOC}"
# for HOSTNAME in ${HOSTS} ; do
#     ssh -l ${USERNAME} ${HOSTNAME} "${SCRIPT}"
# done

# scp -r ${USERNAME}@${HOSTNAME}:/home/${USERNAME}/${RASPBERRY_PI_VIDEO_NAME} ${LOCAL_FILE_SAVE}

#!/bin/bash
USERNAME=riki
HOSTS="10.194.88.166"
SCRIPT="pwd; source bme436-final/bin/activate; sudo bme436-final/bin/python /home/riki/strandtest3.py"
for HOSTNAME in ${HOSTS} ; do
    ssh -l ${USERNAME} ${HOSTNAME} "${SCRIPT}"
done


scp -r riki@10.194.88.166:/home/riki/test_video_random.mp4 /Users/devinshah/Downloads/

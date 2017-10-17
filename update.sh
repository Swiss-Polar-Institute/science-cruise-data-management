rsync -r -l -z -t --delete --delete-excluded --filter='+ */' --filter='- *.pyc' ScienceCruiseDataManagement/ /var/www/vhosts/scdm.epfl.ch/private/ScienceCruiseDataManagement/

rsync -r -l -z -t --delete --delete-excluded --filter='+ */' --filter='- *.pyc' requirements.txt /var/www/vhosts/scdm.epfl.ch/private/requirements.txt

rsync -r -l -z -t --delete --delete-excluded --filter='+ */' --filter='- *.pyc' scdm.conf /var/www/vhosts/scdm.epfl.ch/conf/scdm.conf

ln -sf /var/www/vhosts/scdm.epfl.ch/private/ScienceCruiseDataManagement/ScienceCruiseDataManagement/settings_prod.py /var/www/vhosts/scdm.epfl.ch/private/ScienceCruiseDataManagement/ScienceCruiseDataManagement/default.py

source /opt/rh/rh-python35/enable
source /var/www/vhosts/scdm.epfl.ch/private/virtenv/scdm-env/bin/activate

pip install -r /var/www/vhosts/scdm.epfl.ch/private/requirements.txt

python /var/www/vhosts/scdm.epfl.ch/private/ScienceCruiseDataManagement/manage.py collectstatic

sudo systemctl restart httpd24-httpd

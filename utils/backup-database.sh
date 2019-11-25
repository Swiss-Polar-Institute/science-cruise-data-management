#!/bin/bash

if [ ! -n "$1" ]
then
	echo "Please provide directory to export the database to"
	exit 1
fi


if [ ! -d "$1" ]
then
	echo "$1 needs to be a directory"
	exit 1
fi

if [ ! -n "$2" ]
then
	echo "Please provide rclone.conf file (mandatory, to upload the file somewhere)"
	exit 1
fi

if [ ! -n "$3" ]
then
	echo "Please provide the dest:path in rclone"
	exit 1
fi

OUTPUT_DIRECTORY="$1"
RCLONE_CONFIG="$2"
RCLONE_DEST_PATH="$3"

DATETIME="$(date +%Y%m%d-%H%M%S)"

OUTPUT_FILE="$OUTPUT_DIRECTORY/science-cruise-data-management-$DATETIME.sql.gz"
docker exec science-cruise-data-management_science-cruise-data-management_1 mysqldump --defaults-file=/var/run/secrets/science_cruise_data_management_mysql.conf scdm | gzip > "$OUTPUT_FILE"
echo "$OUTPUT_FILE"

rclone --config="$RCLONE_CONFIG" copy "$OUTPUT_FILE" "$RCLONE_DEST_PATH"

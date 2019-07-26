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

OUTPUT_DIRECTORY="$1"

DATETIME="$(date +%Y%m%d-%H%M%S)"

OUTPUT_FILE="$OUTPUT_DIRECTORY/spi-media-gallery-$DATETIME.sql.gz"
docker exec spi-media-gallery_spi-media-gallery_1 mysqldump --defaults-file=/run/secrets/spi_media_gallery_mysql.conf spi_media_gallery | gzip > "$OUTPUT_FILE"

echo "Dumped $OUTPUT_FILE.gz"

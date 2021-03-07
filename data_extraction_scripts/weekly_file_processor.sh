#!/bin/bash

function print_usage {
    printf "\n<PATH>/data_extraction_scripts/file_processor.sh\n"
    printf "\t--download\t\t\tDownload the weekly datasets from aws\n"
    printf "\t--extract\t\tExtract the files from the gz\n"
    printf "\t--process\t\tProcess the extracted csv files\n"
    printf "\t--help\t\t\tPrint this list\n\n"
}

function download_files() {
    printf "Downloading files\n"
    mkdir "data/raw"
    files=(
    "2019-01-07-weekly-patterns.csv.gz"
    "2019-02-04-weekly-patterns.csv.gz"
    "2019-03-04-weekly-patterns.csv.gz"
    "2019-04-01-weekly-patterns.csv.gz"
    "2019-05-06-weekly-patterns.csv.gz"
    "2019-06-03-weekly-patterns.csv.gz"
    "2019-07-01-weekly-patterns.csv.gz"
    "2019-08-05-weekly-patterns.csv.gz"
    "2019-09-02-weekly-patterns.csv.gz"
    "2019-10-07-weekly-patterns.csv.gz"
    "2019-11-04-weekly-patterns.csv.gz"
    "2019-12-02-weekly-patterns.csv.gz"
    )
    for filename in "${files[@]}" ; do
        cmd="aws s3 cp s3://sg-c19-response/weekly-patterns/v2/main-file/$filename .data/raw/ --profile safegraphws --endpoint https://s3.wasabisys.com"
        eval "$cmd"
    done
    printf "Done\n\n";
}

function extract_files() {
    printf "Extracting files\n"
    mkdir "data/extracted"
    files=($(ls data/raw/*.csv.gz | xargs -n 1 basename))
    for filename in "${files[@]}" ; do
        printf "Extracting $filename\n"
        gzip -dk "data/raw/$filename"
    done
    mv raw/*.csv extracted 
    printf "Done\n\n";
}

function process_files() {
    printf "Processing files\n"
    mkdir "data/processed"
    files=($(ls data/extracted/*.csv | xargs -n 1 basename))
    for filename in "${files[@]}" ; do
        printf "Processing $filename\n"
        python3 data_extraction_scripts_processor.py "data/extracted/$filename" "data/processed/$filename" "data/additional_data/ny_metro_area_zip_codes.csv"
    done
    printf "Done\n\n";
}

if [[ $# -lt 0 ]] ; then
    print_usage
    exit
fi

while [[ $# -gt 0 ]] ; do
    key="$1"
    case "$key" in
        "--download")
            download=1
            ;;
        "--extract")
            extract=1
            ;;
        "--process")
            process=1
            ;;
        "--help"|*)
            print_usage
            exit
            ;;
    esac
    shift
done

mkdir "data"

if [ "$download" == "1" ] ; then
    download_files
fi

if [ "$extract" == "1" ] ; then
    extract_files
fi

if [ "$process" == "1" ] ; then
    process_files
fi

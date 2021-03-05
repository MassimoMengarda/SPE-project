#!/bin/bash


function print_usage {
    printf "\n<PATH>/file_processor.sh\n"
    printf "\t--download\t\t\tDownload the weekly datasets from aws\n"
    printf "\t--extract\t\tExtract the files from the gz\n"
    printf "\t--help\t\t\tPrint this list\n\n"
}

function download_files() {
    printf "Downloading files\n"
    mkdir "raw"
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
        cmd="aws s3 cp s3://sg-c19-response/weekly-patterns/v2/main-file/$filename ./raw/ --profile safegraphws --endpoint https://s3.wasabisys.com"
        eval "$cmd"
    done
    printf "Done\n\n";
}

function extract_files() {
    printf "Extracting files\n"
    mkdir "extracted"
    files=($(ls raw/*.csv.gz | xargs -n 1 basename))
    for filename in "${files[@]}" ; do
        printf "Extracting $filename\n"
        gzip -dk "raw/$filename"
    done
    mv raw/*.csv extracted 
    printf "Done\n\n";
}

function process_files() {
    printf "Processing files\n"
    mkdir "processed"
    files=($(ls extracted/*.csv | xargs -n 1 basename))
    for filename in "${files[@]}" ; do
        printf "Processing $filename\n"
        python3 processor.py "extracted/$filename" "processed/$filename"
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

if [ "$download" == "1" ] ; then
    download_files
fi

if [ "$extract" == "1" ] ; then
    extract_files
fi

if [ "$process" == "1" ] ; then
    process_files
fi


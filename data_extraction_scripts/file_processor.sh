#!/bin/bash

function print_usage {
    printf "\n<PATH>/data_extraction_scripts/file_processor.sh\n"
    printf "\t--download\t\t\tDownload the weekly datasets from aws\n"
    printf "\t--extract\t\tExtract the files from the gz\n"
    printf "\t--process\t\tProcess the extracted csv files\n"
    printf "\t--help\t\t\tPrint this list\n\n"
}

function download_weekly_files() {
    printf "Downloading weekly files\n"
    mkdir "data/raw"
    mkdir "data/raw/weekly"
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
        cmd="aws s3 cp s3://sg-c19-response/weekly-patterns/v2/main-file/$filename data/raw/weekly/ --profile safegraphws --endpoint https://s3.wasabisys.com"
        eval "$cmd"
    done
    printf "Done\n\n";
}

function download_core_poi_files() {
    printf "Downloading core poi files\n"
    mkdir "data/raw"
    mkdir "data/raw/core_poi"
    files=(
    "core_poi-part1.csv.gz"
    "core_poi-part2.csv.gz"
    "core_poi-part3.csv.gz"
    "core_poi-part4.csv.gz"
    "core_poi-part5.csv.gz"
    )
    for filename in "${files[@]}" ; do
        cmd="aws s3 cp s3://sg-c19-response/core-places-delivery/core_poi/2020/11/06/12/$filename data/raw/core_poi/ --profile safegraphws --endpoint https://s3.wasabisys.com"
        eval "$cmd"
    done
    printf "Done\n\n";
}

function extract_weekly_files() {
    printf "Extracting weekly files\n"
    mkdir "data/extracted"
    mkdir "data/extracted/weekly"
    files=($(ls data/raw/weekly/*.csv.gz | xargs -n 1 basename))
    for filename in "${files[@]}" ; do
        printf "Extracting $filename\n"
        gzip -dk "data/raw/weekly/$filename"
    done
    mv data/raw/weekly/*.csv data/extracted/weekly
    printf "Done\n\n";
}

function extract_core_poi_files() {
    printf "Extracting core poi files\n"
    mkdir "data/extracted"
    mkdir "data/extracted/core_poi"
    files=($(ls data/raw/core_poi/*.csv.gz | xargs -n 1 basename))
    for filename in "${files[@]}" ; do
        printf "Extracting $filename\n"
        gzip -dk "data/raw/core_poi/$filename"
    done
    mv data/raw/core_poi/*.csv data/extracted/core_poi
    printf "Done\n\n";
}

function process_core_poi_files() {
    printf "Processing core poi files\n"
    mkdir "data/processed"
    mkdir "data/processed/core_poi"

    python3 data_extraction_scripts/core_poi_files_concat_filter.py "data/extracted/core_poi" "data/additional_data/ny_metro_area_zip_codes.csv" "data/processed/core_poi/core_poi.csv" 

    printf "Done\n\n";
}

function process_weekly_files() {
    printf "Processing weekly files\n"
    mkdir "data/processed"
    mkdir "data/processed/weekly"

    files=($(ls data/extracted/weekly/*.csv | xargs -n 1 basename))
    for filename in "${files[@]}" ; do
        printf "Processing $filename\n"
        #python3 data_extraction_scripts/weekly_file_filter.py "data/extracted/weekly/$filename" "data/additional_data/ny_metro_area_zip_codes_no_duplicate.csv" "data/processed/weekly/$filename"
        python3 data_extraction_scripts/core_poi_file_join_weekly.py "data/processed/core_poi/core_poi.csv" "data/processed/weekly/$filename" "data/processed/weekly/$filename"
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
    read -p "Download weekly files? [y|n]" answer
    if [ "$answer" == "y" ] ; then
        download_weekly_files
    fi

    read -p "Download core poi files? [y|n]" answer
    if [ "$answer" == "y" ] ; then
        download_core_poi_files
    fi
fi

if [ "$extract" == "1" ] ; then
    read -p "Extract weekly files? [y|n]" answer
    if [ "$answer" == "y" ] ; then
        extract_weekly_files
    fi
        
    read -p "Extract core poi files? [y|n]" answer
    if [ "$answer" == "y" ] ; then
        extract_core_poi_files
    fi
fi

if [ "$process" == "1" ] ; then
    read -p "Process core poi files? [y|n]" answer
    if [ "$answer" == "y" ] ; then
        process_core_poi_files
    fi

    read -p "Process weekly files? [y|n]" answer
    if [ "$answer" == "y" ] ; then
        process_weekly_files
    fi
fi

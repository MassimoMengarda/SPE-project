#!/bin/bash

function print_usage {
    printf "\n<PATH>/data_extraction_and_preprocessing/file_processor.sh\n"
    printf "\t--download\t\t\tDownload the weekly datasets from aws\n"
    printf "\t--extract\t\tExtract the files from the gz\n"
    printf "\t--process\t\tProcess the extracted csv files\n"
    printf "\t--help\t\t\tPrint this list\n\n"
}

function download_weekly_files() {
    printf "Downloading weekly files\n"
    dir="data/raw/weekly"
    mkdir -p "$dir"
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
        cmd="aws s3 cp s3://sg-c19-response/weekly-patterns/v2/main-file/$filename $dir/ --profile safegraphws --endpoint https://s3.wasabisys.com"
        eval "$cmd"
    done
    printf "Done\n\n";
}

function download_core_poi_files() {
    printf "Downloading core poi files\n"
    dir="data/raw/core_poi"
    mkdir -p "$dir"
    files=(
    "core_poi-part1.csv.gz"
    "core_poi-part2.csv.gz"
    "core_poi-part3.csv.gz"
    "core_poi-part4.csv.gz"
    "core_poi-part5.csv.gz"
    )
    for filename in "${files[@]}" ; do
        cmd="aws s3 cp s3://sg-c19-response/core-places-delivery/core_poi/2020/11/06/12/$filename $dir/ --profile safegraphws --endpoint https://s3.wasabisys.com"
        eval "$cmd"
    done
    printf "Done\n\n";
}

function download_home_summary_files() {
    printf "Downloading home summary files\n"
    dir="data/extracted/home_summary"
    mkdir -p "$dir"
    files=(
    "2019-01-07-home-panel-summary.csv"
    "2019-02-04-home-panel-summary.csv"
    "2019-03-04-home-panel-summary.csv"
    "2019-04-01-home-panel-summary.csv"
    "2019-05-06-home-panel-summary.csv"
    "2019-06-03-home-panel-summary.csv"
    "2019-07-01-home-panel-summary.csv"
    "2019-08-05-home-panel-summary.csv"
    "2019-09-02-home-panel-summary.csv"
    "2019-10-07-home-panel-summary.csv"
    "2019-11-04-home-panel-summary.csv"
    "2019-12-02-home-panel-summary.csv"
    )
    for filename in "${files[@]}" ; do
        cmd="aws s3 cp s3://sg-c19-response/weekly-patterns/v2/home-summary-file/$filename $dir/ --profile safegraphws --endpoint https://s3.wasabisys.com"
        eval "$cmd"
    done
    printf "Done\n\n";
}

function download_social_distancing_files() {
    printf "Downloading social distancing files\n"
    dir="data/raw/social_distancing"
    mkdir -p "$dir"
    file="social-distancing.csv.gz"
    dates=(
    "2019-01-07"
    "2019-02-04"
    "2019-03-04"
    "2019-04-01"
    "2019-05-06"
    "2019-06-03"
    "2019-07-01"
    "2019-08-05"
    "2019-09-02"
    "2019-10-07"
    "2019-11-04"
    "2019-12-02"
    )
    for date in "${dates[@]}" ; do
        for i in {0..6} ; do
            dirdate=$(date +%Y/%m/%d -d "$date +$i days")
            filedate=$(date +%Y-%m-%d -d "$date +$i days")
            filename="$filedate-$file"
            cmd="aws s3 cp s3://sg-c19-response/social-distancing/v2/$dirdate/$filename $dir/ --profile safegraphws --endpoint https://s3.wasabisys.com"
            eval "$cmd"
        done
    done
    printf "Done\n\n";
}

function extract_weekly_files() {
    printf "Extracting weekly files\n"
    from="data/raw/weekly"
    to="data/extracted/weekly"
    mkdir -p "$to"
    files=($(ls $from/*.csv.gz | xargs -n 1 basename))
    for filename in "${files[@]}" ; do
        printf "Extracting $filename\n"
        gzip -dk "$from/$filename"
    done
    mv $from/*.csv $to
    printf "Done\n\n";
}

function extract_core_poi_files() {
    printf "Extracting core poi files\n"
    from="data/raw/core_poi"
    to="data/extracted/core_poi"
    mkdir -p "$to"
    files=($(ls $from/*.csv.gz | xargs -n 1 basename))
    for filename in "${files[@]}" ; do
        printf "Extracting $filename\n"
        gzip -dk "$from/$filename"
    done
    mv $from/*.csv $to
    printf "Done\n\n";
}

function extract_social_distancing_files() {
    printf "Extracting social distancing files\n"
    from="data/raw/social_distancing"
    to="data/extracted/social_distancing"
    mkdir -p "$to"
    files=($(ls $from/*.csv.gz | xargs -n 1 basename))
    for filename in "${files[@]}" ; do
        printf "Extracting $filename\n"
        gzip -dk "$from/$filename"
    done
    mv $from/*.csv $to
    printf "Done\n\n";
}

function process_core_poi_files() {
    printf "Processing core poi files\n"
    from="data/extracted/core_poi"
    to="data/processed/core_poi"
    mkdir -p "$to"
    python3 data_extraction_and_preprocessing/core_poi_files_concat_filter.py "$from" "data/additional_data/ny_metro_area_zip_codes.csv" "$to/core_poi.csv" 
    printf "Done\n\n";
}

function process_weekly_files() {
    printf "Processing weekly files\n"
    from="data/extracted/weekly"
    to="data/processed/weekly"
    mkdir -p "$to"

    files=($(ls $from/*.csv | xargs -n 1 basename))
    for filename in "${files[@]}" ; do
        printf "Processing $filename\n"
        python3 data_extraction_and_preprocessing/weekly_file_filter.py "$from/$filename" "data/additional_data/ny_metro_area_zip_codes_no_duplicate.csv" "$to/$filename"
        python3 data_extraction_and_preprocessing/core_poi_file_join_weekly.py "data/processed/core_poi/core_poi.csv" "$to/$filename" "$to/$filename"
    done
    printf "Done\n\n";
}

function process_home_summary_files() {
    printf "Processing home summary files\n"
    from="data/extracted/home_summary"
    to="data/processed/home_summary"
    mkdir -p "$to"
    python3 data_extraction_and_preprocessing/home_summary_filter.py "$from" "data/additional_data/zip_cbg_join_filtered.csv" "$to" 
    printf "Done\n\n";
}

function process_social_distancing_files() {
    printf "Processing social distancing files\n"
    from="data/extracted/social_distancing"
    to="data/processed/social_distancing"
    mkdir -p "$to"
    python3 data_extraction_and_preprocessing/social_distancing_filter.py "$from" "data/additional_data/zip_cbg_join_filtered.csv" "$to" 
    printf "Done\n\n";
}

function process_population_files() {
    printf "Processing population files\n"
    from="data/additional_data/safegraph_open_census_data"
    to="data/processed/population"
    mkdir -p "$to"
    python3 data_extraction_and_preprocessing/population_filter.py "$from" "data/additional_data/zip_cbg_join_filtered.csv" "$to" 
    printf "Done\n\n";
}

if [[ $# -lt 0 ]] ; then
    print_usage
    exit
fi

while [[ $# -gt 0 ]] ; do
    key="$1"
    case "$key" in
        "--download"|"-d")
            download=1
            ;;
        "--extract"|"-e")
            extract=1
            ;;
        "--process"|"-p")
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
    read -rp "Download weekly files? [y|n]" answer
    if [ "$answer" == "y" ] ; then
        download_weekly_files
    fi

    read -rp "Download core poi files? [y|n]" answer
    if [ "$answer" == "y" ] ; then
        download_core_poi_files
    fi

    read -rp "Download home summary files? [y|n]" answer
    if [ "$answer" == "y" ] ; then
        download_home_summary_files
    fi

    read -rp "Download social distancing files? [y|n]" answer
    if [ "$answer" == "y" ] ; then
        download_social_distancing_files
    fi
fi

if [ "$extract" == "1" ] ; then
    read -rp "Extract weekly files? [y|n]" answer
    if [ "$answer" == "y" ] ; then
        extract_weekly_files
    fi
        
    read -rp "Extract core poi files? [y|n]" answer
    if [ "$answer" == "y" ] ; then
        extract_core_poi_files
    fi
        
    read -rp "Extract social distancing files? [y|n]" answer
    if [ "$answer" == "y" ] ; then
        extract_social_distancing_files
    fi
fi

if [ "$process" == "1" ] ; then
    read -rp "Process core poi files? [y|n]" answer
    if [ "$answer" == "y" ] ; then
        process_core_poi_files
    fi

    read -rp "Process weekly files? [y|n]" answer
    if [ "$answer" == "y" ] ; then
        process_weekly_files
    fi

    read -rp "Process social distancing files? [y|n]" answer
    if [ "$answer" == "y" ] ; then
        process_social_distancing_files
    fi

    read -rp "Process home summary files? [y|n]" answer
    if [ "$answer" == "y" ] ; then
        process_home_summary_files
    fi

    read -rp "Process population files? [y|n]" answer
    if [ "$answer" == "y" ] ; then
        process_population_files
    fi
fi

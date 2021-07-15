#!/bin/bash

dates=(
"2020-03-02"
"2020-03-09"
"2020-03-16"
"2020-03-23"
"2020-03-30"
"2020-04-06"
"2020-04-13"
"2020-04-20"
"2020-04-27"
)

function print_usage {
    printf "\n<PATH>/data_extraction_and_preprocessing/file_processor.sh\n"
    printf "\t--download | d\t\tDownload the weekly datasets from aws\n"
    printf "\t--extract | e\t\tExtract the files from the gz\n"
    printf "\t--process | p\t\tProcess the extracted csv files\n"
    printf "\t--automatic | a\t\tDo not wait for user answer csv files\n"
    printf "\t--help\t\t\tPrint this list\n\n"
}

function download_weekly_files() {
    printf "Downloading weekly files\n"
    dir="data/raw/weekly"
    mkdir -p "$dir"
    file="weekly-patterns.csv.gz"

    for date in "${dates[@]}" ; do
        cmd="aws s3 cp s3://sg-c19-response/weekly-patterns/v2/main-file/$date-$file $dir/ --profile safegraphws --endpoint https://s3.wasabisys.com"
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
    file="home-panel-summary.csv"
    for date in "${dates[@]}" ; do
        cmd="aws s3 cp s3://sg-c19-response/weekly-patterns/v2/home-summary-file/$date-$file $dir/ --profile safegraphws --endpoint https://s3.wasabisys.com"
        eval "$cmd"
    done
    printf "Done\n\n";
}

function download_social_distancing_files() {
    printf "Downloading social distancing files\n"
    dir="data/raw/social_distancing"
    mkdir -p "$dir"
    file="social-distancing.csv.gz"

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
    python3 -m data_extraction_and_preprocessing.preprocessing.core_poi_files_concat_filter "$from" "data/additional_data/ny_metro_area_zip_codes.csv" "$to/core_poi.csv" 
    printf "Done\n\n";
}

function process_weekly_files() {
    printf "Processing weekly files\n"
    from="data/extracted/weekly"
    to="data/processed/weekly"
    mkdir -p "$to"
    python3 -m data_extraction_and_preprocessing.preprocessing.weekly_file_filter "$from" "data/additional_data/ny_metro_area_zip_codes.csv" "$to"
    printf "Done\n\n";
}

function process_home_summary_files() {
    printf "Processing home summary files\n"
    from="data/extracted/home_summary"
    to="data/processed/home_summary"
    mkdir -p "$to"
    python3 -m data_extraction_and_preprocessing.preprocessing.home_summary_filter "$from" "data/additional_data/zip_cbg_join_filtered.csv" "$to" 
    printf "Done\n\n";
}

function process_social_distancing_files() {
    printf "Processing social distancing files\n"
    from="data/extracted/social_distancing"
    to="data/processed/social_distancing"
    mkdir -p "$to"
    python3 -m data_extraction_and_preprocessing.preprocessing.social_distancing_filter "$from" "data/additional_data/zip_cbg_join_filtered.csv" "$to" 
    printf "Done\n\n";
}

function process_population_files() {
    printf "Processing population files\n"
    from="data/additional_data/safegraph_open_census_data"
    to="data/processed/population"
    mkdir -p "$to"
    python3 -m data_extraction_and_preprocessing.preprocessing.population_filter "$from" "data/additional_data/zip_cbg_join_filtered.csv" "$to" 
    printf "Done\n\n";
}

function read_answer() {
    local title="$1"
    local answer=1
    if [ "$automatic" != "1" ]; then
        read -rp "$title" tmp

        if [ "$tmp" != "y" ]; then
            local answer=0
        fi
    fi
    return "$answer"
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
        "--automatic"|"-a")
            automatic=1
            ;;
        "--help"|*)
            print_usage
            exit
            ;;
    esac
    shift
done

if [ "$download" == "1" ] ; then
    read_answer "Download weekly files? [y|n]"
    answer="$?"
    if [ "$answer" == "1" ] ; then
        download_weekly_files
    fi

    read_answer "Download core poi files? [y|n]"
    answer="$?"
    if [ "$answer" == "1" ] ; then
        download_core_poi_files
    fi

    read_answer "Download home summary files? [y|n]"
    answer="$?"
    if [ "$answer" == "1" ] ; then
        download_home_summary_files
    fi

    read_answer "Download social distancing files? [y|n]"
    answer="$?"
    if [ "$answer" == "1" ] ; then
        download_social_distancing_files
    fi
fi

if [ "$extract" == "1" ] ; then
    read_answer "Extract weekly files? [y|n]"
    answer="$?"
    if [ "$answer" == "1" ] ; then
        extract_weekly_files
    fi
        
    read_answer "Extract core poi files? [y|n]"
    answer="$?"
    if [ "$answer" == "1" ] ; then
        extract_core_poi_files
    fi
        
    read_answer "Extract social distancing files? [y|n]"
    answer="$?"
    if [ "$answer" == "1" ] ; then
        extract_social_distancing_files
    fi
fi

if [ "$process" == "1" ] ; then
    read_answer "Process core poi files? [y|n]"
    answer="$?"
    if [ "$answer" == "1" ] ; then
        process_core_poi_files
    fi

    read_answer "Process weekly files? [y|n]"
    answer="$?"
    if [ "$answer" == "1" ] ; then
        process_weekly_files
    fi

    read_answer "Process social distancing files? [y|n]"
    answer="$?"
    if [ "$answer" == "1" ] ; then
        process_social_distancing_files
    fi

    read_answer "Process home summary files? [y|n]"
    answer="$?"
    if [ "$answer" == "1" ] ; then
        process_home_summary_files
    fi

    read_answer "Process population files? [y|n]"
    answer="$?"
    if [ "$answer" == "1" ] ; then
        process_population_files
    fi
fi

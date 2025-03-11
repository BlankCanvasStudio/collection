#!/bin/bash


DIR=""
declare -A UNITS
UNITS=( ["K"]=1000 ["M"]=1000000)


show_help() {
    echo -e "Usage: ./database-files.sh [options] <experiment results root>"
    echo -e ""
    echo -e "This program calculates the average size of the databases for a series of experiments"
    echo -e "It assumes the structure <path to exp>/<exp name>/<trial no>"
    echo -e ""
    echo -e "<experiment results root> should be of the form: <path to exp>/<exp name>"
    echo -e ""
    echo -e "Options:"
    echo -e "-h | --help shows this menu"
    echo -e ""
}


while [[ $# -gt 0 ]]; do
    case $1 in
        -h | --help)
            show_help
            shift
            ;;
        *)
            if [ ! "$DIR" = "" ]; then
                echo "Unknown parameter: $1. Dir already specified as $DIR"
                echo "Exiting..."
                exit 1
            fi

            DIR="$1"
            shift
            ;;
    esac
done


if [ "$DIR" = "" ]; then
    echo ""
    echo "Please specify an experiment directory!"
    echo ""
    show_help
    exit 1
fi


NUM_TRIALS=$(ls $DIR | wc -l)


POSTGRES_TOTAL=0
INFLUX_TOTAL=0


for TRIAL in $(ls $DIR); do
    EXP="$DIR/$TRIAL"

    POSTGRES_SIZE_STR=`ls -lh $DIR/$TRIAL | grep postgres | awk '{print $5}'`
    INFLUX_SIZE_STR=`ls -lh $DIR/$TRIAL | grep influx | awk '{print $5}'`

    if [ "$POSTGRES_SIZE_STR" = "" ] || [ "$INFLUX_SIZE_STR" = "" ]; then
        continue;
    fi


    POSTGRES_SIZE_INT=$(bc -l <<< "${POSTGRES_SIZE_STR%%[A-Z]*} * ${UNITS[${POSTGRES_SIZE_STR##*[0-9]}]}")
    INFLUX_SIZE_INT=$(bc -l <<< "${INFLUX_SIZE_STR%%[A-Z]*} * ${UNITS[${INFLUX_SIZE_STR##*[0-9]}]}")

    POSTGRES_TOTAL=$(bc -l <<< "$POSTGRES_TOTAL + $POSTGRES_SIZE_INT")
    INFLUX_TOTAL=$(bc -l <<< "$INFLUX_TOTAL + $INFLUX_SIZE_INT")

done


echo ""
echo "Average postgres size: $(bc -l <<< "scale=2;$POSTGRES_TOTAL / $NUM_TRIALS") Bytes"
echo ""
echo "Average influx size: $(bc -l <<< "scale=2;$INFLUX_TOTAL / $NUM_TRIALS") Bytes"
echo ""


#!/usr/bin/env bash

HERE=$(cd `dirname $0`; pwd)
ROOT=$HERE/

wSZ_app_IP="172.16.37.8"
wSZ_app_port=8080

sig_srv_IP="172.16.37.9"
sig_srv_port=8089

nr_players=3;
player_id=-1;
protocol=0; # 0 = shamir, 1 = rep-ring, ...
array_size=100000;

#Start execution
if [ $# -eq 4 ]; then
    nr_players=$1;
    player_id=$2;
    protocol=$3;
    array_size=$4;
else
    echo "Usage: ./run...single.sh [Number of Players] [Player ID] [Protocol (0=shamir, 1=rep-ring), [ArraySize (100, 1000, 10 000, 100 000)]]";
    echo "       // Note: Player Number for Replicated Ring Protocol is fixed to 3 Players"
    exit -1;
fi

# Starting the browser
file="Logs/party_${player_id}.log"
echo ".. Player $player_id: Running computation with protocol $protocol (0=Shamir, 1=Rep3Ring, 2=Rep4Ring, ..), $nr_players parties and array size $array_size" > $file;
# if [ $protocol -eq 0 ]; then
#   python3 execute.py "https://$wSZ_app_IP:$wSZ_app_port/Shamir/128-bit-$array_size/shamir-party.html?arguments=-N,$nr_players,-w,-ss,$sig_srv_IP:$sig_srv_port,$player_id,innerprod" > $file 2>&1 &
#   # python3 execute.py "https://$wSZ_app_IP:$wSZ_app_port/Shamir/128-bit-$array_size/shamir-party.html?arguments=-N,$nr_players,-w,-ss,$sig_srv_IP:$sig_srv_port,$player_id,innerprod" 2>&1 &
# else
#   python3 execute.py "https://$wSZ_app_IP:$wSZ_app_port/Rep-Ring/128-bit-$array_size/replicated-ring-party.html?arguments=-w,-ss,$sig_srv_IP:$sig_srv_port,$player_id,innerprod" > $file 2>&1 &
#   # python3 execute.py "https://$wSZ_app_IP:$wSZ_app_port/Rep-Ring/128-bit-$array_size/replicated-ring-party.html?arguments=-w,-ss,$sig_srv_IP:$sig_srv_port,$player_id,innerprod" 2>&1 &
# fi
case $protocol in
0) echo "Shamir Passive" >> $file 2>&1; 
  pipenv run python3 execute.py "https://$wSZ_app_IP:$wSZ_app_port/Shamir/128-bit-$array_size/shamir-party.html?arguments=-N,$nr_players,-w,0,-ss,$sig_srv_IP:$sig_srv_port,$player_id,innerprod" >> $file 2>&1 & ;;
1) echo "Rep R." >> $file 2>&1;
  pipenv run python3 execute.py "https://$wSZ_app_IP:$wSZ_app_port/Rep-Ring/128-bit-$array_size/replicated-ring-party.html?arguments=-w,0,-ss,$sig_srv_IP:$sig_srv_port,$player_id,innerprod" >> $file 2>&1 & ;;
2) echo "Rep4 R." >> $file 2>&1; 
  pipenv run python3 execute.py "https://$wSZ_app_IP:$wSZ_app_port/Rep4-Ring/128-bit-$array_size/rep4-ring-party.html?arguments=-w,0,-ss,$sig_srv_IP:$sig_srv_port,$player_id,innerprod" >> $file 2>&1 & ;;
3) echo "Shamir-ML-Eval" >> $file 2>&1; 
  pipenv run python3 execute.py "https://$wSZ_app_IP:$wSZ_app_port/Shamir/ML-Eval/shamir-party.html?arguments=--batch-size,64,-N,$nr_players,-w,0,-ss,$sig_srv_IP:$sig_srv_port,$player_id,breast_logistic_eval" >> $file 2>&1 & ;;
4) echo "Shamir-ML-Training" >> $file 2>&1; 
  pipenv run python3 execute.py "https://$wSZ_app_IP:$wSZ_app_port/Shamir/ML-Training/shamir-party.html?arguments=--batch-size,64,-N,$nr_players,-w,0,-ss,$sig_srv_IP:$sig_srv_port,$player_id,breast_logistic_train" >> $file 2>&1 & ;;
5) echo "RepRing-ML-Eval" >> $file 2>&1; 
  pipenv run python3 execute.py "https://$wSZ_app_IP:$wSZ_app_port/Rep-Ring/ML-Eval/replicated-ring-party.html?arguments=--batch-size,64,-N,$nr_players,-w,0,-ss,$sig_srv_IP:$sig_srv_port,$player_id,breast_logistic_eval" >> $file 2>&1 & ;;
6) echo "RepRing-ML-Training" >> $file 2>&1; 
  pipenv run python3 execute.py "https://$wSZ_app_IP:$wSZ_app_port/Rep-Ring/ML-Training/replicated-ring-party.html?arguments=--batch-size,64,-N,$nr_players,-w,0,-ss,$sig_srv_IP:$sig_srv_port,$player_id,breast_logistic_train" >> $file 2>&1 & ;;
7) echo "Rep4Ring-ML-Eval" >> $file 2>&1; 
  pipenv run python3 execute.py "https://$wSZ_app_IP:$wSZ_app_port/Rep4-Ring/ML-Eval/rep4-ring-party.html?arguments=--batch-size,64,-N,$nr_players,-w,0,-ss,$sig_srv_IP:$sig_srv_port,$player_id,breast_logistic_eval" >> $file 2>&1 & ;;
8) echo "Rep4Ring-ML-Training" >> $file 2>&1; 
  pipenv run python3 execute.py "https://$wSZ_app_IP:$wSZ_app_port/Rep4-Ring/ML-Training/rep4-ring-party.html?arguments=--batch-size,64,-N,$nr_players,-w,0,-ss,$sig_srv_IP:$sig_srv_port,$player_id,breast_logistic_train" >> $file 2>&1 & ;;
*) echo "Protocol ID $Protocol not supported yet" >> $file 2>&1; exit;;
esac

pid=$!
wait $pid

  # if [ $Program -eq 0 ]; then
  #   python3 execute.py "https://$wSZ_app_IP:$wSZ_app_port/Shamir/ML-Training/shamir-party.html?arguments=--batch-size,64,-N,$nr_players,-w,0,-ss,$sig_srv_IP:$sig_srv_port,$i,breast_logistic_train" > $file 2>&1 &
  # else
  #   python3 execute.py "https://$wSZ_app_IP:$wSZ_app_port/Shamir/ML-Eval/shamir-party.html?arguments=--batch-size,64,-N,$nr_players,-w,0,-ss,$sig_srv_IP:$sig_srv_port,$i,breast_logistic_train" > $file 2>&1 &
  # fi ;;

# open file and read results
# check_time=$(head -n 1 $file)
# echo -n "Player-$player_id($check_time) "
# echo
# echo "Result: $(head -n 2 $file | tail -n 1)"

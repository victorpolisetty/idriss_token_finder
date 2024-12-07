if test -d credit_score_agent; then
  echo "Removing previous agent build"
  rm -r credit_score_agent
fi

source .env

find . -empty -type d -delete  # remove empty directories to avoid wrong hashes
autonomy packages lock
autonomy fetch --local --agent victorpolisetty/credit_score_agent && cd credit_score_agent

cp $PWD/../ethereum_private_key.txt .
autonomy add-key ethereum ethereum_private_key.txt
autonomy issue-certificates
aea -s run
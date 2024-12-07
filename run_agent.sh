if test -d idriss_token_finder_agent; then
  echo "Removing previous agent build"
  rm -r idriss_token_finder_agent
fi

source .env

find . -empty -type d -delete  # remove empty directories to avoid wrong hashes
autonomy packages lock
autonomy fetch --local --agent victorpolisetty/idriss_token_finder_agent && cd idriss_token_finder_agent

cp $PWD/../ethereum_private_key.txt .
autonomy add-key ethereum ethereum_private_key.txt
autonomy issue-certificates
aea -s run
# betterhacker.news

https://betterhacker.news


# To run
```bash
# Create .env file with OPENAI_TOKEN
vim .env
# -> OPENAI_API_KEY=sk-7xxx7IVfRkqeoxxxxvdDT3BlbkxxVi23VpwdnUO7fIo1D9

pip3 install -r requirements.txt
``` 

Then `uvicorn`
```bash
uvicorn app.app:app --port 5556
```

Then `worker`
```bash
# Run in tmux
while true; do python3 worker.py; ls data/*; sleep 12h; done
```

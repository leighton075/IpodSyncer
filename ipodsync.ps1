param(
    [Parameter(ValueFromRemainingArguments=$true)]
    [string[]]$Args
)

py -3.12 "C:\Users\leigh\Documents\GitHub\IpodSyncer\sync.py" @Args
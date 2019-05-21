macroScript CoronaToClarisse
toolTip: "CoronaToClarisse"
category:"CoronaToClarisse" 
ButtonText:"CoronaToClarisse"
Icon:#("ClarisseIcon",1)
(
path = GetDir #scripts+"\Clarisse\CoronaExport.py"
python.ExecuteFile path
)
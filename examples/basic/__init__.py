
"""
You can obtain your token by logging to your Lumapps account.
Go to https://sites.lumapps.com and authentificate.
Once connected, open the javascript console of your browser and run:


var instance = window.location.pathname.split('/');
instance = instance[instance.length-2];
fetch(window.location.origin+"/service/init?customerHost="+window.location.host+"&instanceSlug="+instance+"&slug=").then(data=>{return data.json()}).then(res => {console.log(res.token)})

This will generate your personal Lumapps token that will be active for 60 minutes and you can put it as the BEARER

"""

BEARER = ""

import requests
import json
import dotenv as d
import os
import base64
from datetime import datetime
# from s3 import WriteToS3

env_file = d.find_dotenv()
d.load_dotenv(env_file)

## will all be in Heroku##Only here for testing###
refreshtoken = os.getenv("refreshtoken")
# print("refreshtoken: ",refreshtoken)
accesstoken = os.getenv("accesstoken")
client_id = os.getenv("client_id")
client_secret = os.getenv("client_secret")
hapikey = os.getenv("hapikey")


utctimee = "2022-03-30T19:15:00Z"


#woo

def gettitleid1(isbn):
    """
    Gets Title Id, Title name and Author name by unique id property - ISBN number

    Args:
        isbn int: The isbn # of a Title

    Returns:
        titleid int: Id of Ayrshare Post
        errors str: any errors with post itself
        title str: title name
        authors str : author name
    """
    # get associations
    url = f'https://api.hubapi.com/crm/v3/objects/Title/{isbn}?archived=false&idProperty=isbnnumber&properties=title_name&properties=author&hapikey={hapikey}'

    headers = {"Content-Type": "application/json"}
    request = requests.get(url)



    if request.status_code != 200:
        errors = "No title found, The ISBN must exist in Hubspot before a promotion is created."
        titleid = None
        title = None
        author = None
        # logger.error(f'HOOTSUITE:ERROR: {errors}")
        print(f"HOOTSUITE:ERROR: {request.text}")
        return titleid, errors, title, author
    else:
        res= request.json()
        titleid = res['id']
        errors=None
        title1 = res['properties']['title_name']
        author = res['properties']['author']
        print(f"HOOTSUITE:SUCCESS: HubSpot API Response: {request.text}")
        # logger.debug(f'HOOTSUITE:SUCCESS: HubSpot API Response: {request.text}')
        return titleid, errors, title1, author


def titlecon2(titleid):
    """
    Seacrhes Hubspot for Contacts associated to Title

    Args:
        titleid str - id returned form titlecon()

    Returns:
        results list - list of associated contact
    """
    url = f'https://api.hubapi.com/crm/v3/objects/Title/{titleid}/associations/Contact?hapikey={hapikey}'
    headers = {"Content-Type": "application/json"}
    res = requests.get(url=url, headers=headers)

    r = res.json()
    results = r['results']


    if res.status_code != 200:
        # logger.error(f'HOOTSUITE:ERROR: No Contact associated to Title:')
        print(f'HOOTSUITE:ERROR: No Contact associated to Title:')
        return None

    if results == []:
        print(f'HOOTSUITE:ERROR: No Contact associated to Title:')
        # logger
    else:
        # print('Search company results', request.text)
        # logger.debug(f'Search company results: {request.text}')
        r = res.json()
        print(f"HOOTSUITE:STATUS: Contacts Associated to Title {results}")
        return results

def gethandle(contactid):
    """
    Gets contact info and social media information

    Args:
        contactid str: Hubspot ContactID


    Returns:
        twitterhandle str:
        fburl str: facebook page url
        first str: firtsname of contact
        last strL lastname of contact
        isauthor bool: HupSpot prop, determine if contact is an author
    """

    url = f'https://api.hubapi.com/crm/v3/objects/contacts/{contactid}?properties=twitter_handle&properties=facebook_page&properties=firstname&properties=lastname&properties=is_author&hapikey={hapikey}'

    headers = {"Content-Type": "application/json"}
    request = requests.get(url)

    if request.status_code != 200:
        errors = "No handles found"
        twitterhandle = None
        fburl = None
        first = None
        last = None
        isauthor= None
        print(f"HOOTSUITE:ERROR: HubSpot API Response: {errors}")
        # logger.error(f"HOOTSUITE:ERROR: HubSpot API Response: {errors}")

        return twitterhandle, fburl, first, last, isauthor, errors
    else:
        res = request.json()
        errors = None
        twitterhandle = res['properties']['twitter_handle']
        fburl= res['properties']['facebook_page']
        first = res['properties']['firstname']
        last= res['properties']['lastname']
        isauthor = res['properties']['is_author']
        print(f"HOOTSUITE:SUCCESS: Contact found: {res}")
        # logger.debug(f"HOOTSUITE:STATUS: Contact found: {res.text}")
        return twitterhandle, fburl, first, last, isauthor, errors


def gettagauthorlist(contactids, platform):
    """
    Takes list of related contactids and retrieves the social media handle, if one isnt available, it grabs the name of the author instead

    Args:
        contactid list: list of contacts ids related to a title

    Returns:
        authors str: a list of author handles based on platform or name if one is not available

    """
    authorlist = []
    length = len(contactids)

    for x in contactids:

        contactid = x['id']
        # contactid = x
        twitterhandle, fburl, first, last, isauthor, errors = gethandle(contactid)
        print(f"HOOTSUITE:STATUS: Checking if Contact is an Author...")
        # edit function for only is author checkbox search hs

        last = last.rstrip(" ")
        if isauthor == 'true':
            if platform == 'Twitter':
                if twitterhandle:
                    print(f"HOOTSUITE:STATUS: Twitter Handle found")

                    if "@" in twitterhandle:
                        twitterhandle = twitterhandle.replace("@","")

                    if length == 1:
                        authorlist.append(f"@{twitterhandle}")
                    elif x == contactids[-1]:
                        authorlist.append(f"and @{twitterhandle}")
                    else:
                        authorlist.append(f"@{twitterhandle}")  # add @ to logic if facebook also does @

                else:
                    if last:
                        if length == 1:
                            authorlist.append(f"{first} {last}")
                        elif x == contactids[-1]:
                            # if last
                            authorlist.append(f"and {first} {last}")
                        else:
                            authorlist.append(f"{first} {last}")
                    else:
                        if length == 1:
                            authorlist.append(f"{first}")
                        elif x == contactids[-1]:
                            # if last
                            authorlist.append(f"and {first}")
                        else:
                            authorlist.append(f"{first}")

            if platform == 'Facebook':
                #fb id fetch package no longer working
                # if fburl:
                #
                #     print(f'checking facebook url: {fburl}')
                #     fbpageid = fbscrape(fburl)
                #
                #     if length == 1:
                #         authorlist.append(f"@[{fbpageid}]")
                #     elif x == contactids[-1]:
                #         authorlist.append(f"and @[{fbpageid}]")
                #     else:
                #         authorlist.append(f"@[{fbpageid}]")  # add @ to logic if facebook also does @

                # else:
                if last:
                    if length == 1:
                        authorlist.append(f"{first} {last}")
                    elif x == contactids[-1]:
                        # if last
                        authorlist.append(f"and {first} {last}")
                    else:
                        authorlist.append(f"{first} {last}")
                else:
                    if length == 1:
                        authorlist.append(f"{first}")
                    elif x == contactids[-1]:
                        # if last
                        authorlist.append(f"and {first}")
                    else:
                        authorlist.append(f"{first}")

            if platform == 'LinkedIn':
                if last:
                    if length == 1:
                        authorlist.append(f"{first} {last}")
                    elif x == contactids[-1]:
                        # if last
                        authorlist.append(f"and {first} {last}")
                    else:
                        authorlist.append(f"{first} {last}")
                else:
                    if length == 1:
                        authorlist.append(f"{first}")
                    elif x == contactids[-1]:
                        # if last
                        authorlist.append(f"and {first}")
                    else:
                        authorlist.append(f"{first}")

    al = ", "
    al = al.join(authorlist)
    print(f"HOOTSUITE:SUCCESS: list of authors created: {al}")
    return al


## add error handling for no handle in hubpsot, end and go to next line
def formatpost(x,contactids,title):
    """
    Formats the post for social media posting. Fills in post with information from csv and hubspot

    Args:
        x (list) - list of dictionaries contain all csv data
        contactids -
        title (str) - name of the title
    Returns:
        formatedpost str - String ready for Social Media Post

    """
    post = x['Social Media Message']
    platform = x['Platform']
    refid = x['Ref ID']
    isbn1 = x["ISBN # - 1"]
    isbn2 = x["ISBN # - 2"]
    isbn3 = x["ISBN # - 3"]
    isbn4 = x["ISBN # - 4"]
    promotype = x['Promotion Type']
    publisher = x['Publisher']
    promolanding = x['Promo Landing Page URL']

    campaign = x['Schedule Post Date']
    timein = x['Scheduled Post Time']
    emailfromname = x['Email From Name']
    emailfromuser = x['Email From User']
    url1 = x['Email promotion cover art URL 1']
    url2 = x['Email promotion cover art URL 2']
    url3 = x['Email promotion cover art URL 3']

    end = x['End Date']
    discount = x['Discount Percent']

    errors = []
    newpost = post

    #format discount
    stringdiscount = ""
    if discount:
        stringdiscount = int(discount)
        stringdiscount = str(stringdiscount)

        if "(discount)" in post:
            # newpost = post.replace('(discount)', discount)
            try:
                newpost = newpost.replace("(discount)", stringdiscount)  # check tagging on facebook and twitter

            except TypeError:
                errors.append("Missing data in the Promotion Type Column")

            if discount == "":
                errors.append("Missing data in the Promotion Type Column")

    #format enddate
    if end:
        newend = end[5:]
        newend = newend.replace("-", "/")
        if "(end)" in post:
            newpost = newpost.replace('(end)', newend)

    #author list
    al = gettagauthorlist(contactids,platform)
    if al:
        newpost = newpost.replace('@', al)

    if "(title)" in post:
        newpost = newpost.replace('(title)', f"\"{title}\"")

    if "(promotion)" in post:
        try:
            newpost = newpost.replace("(promotion)", promotype)  # check tagging on facebook and twitter

        except TypeError:
            errors.append("Missing data in the Promotion Type Column")

        if promotype == "":
            errors.append("Missing data in the Promotion Type Column")


    #shorten if hootsuite does not
    if promolanding != "":
        newpost = newpost + f" {promolanding}"

    print(f"HOOTSUITE:SUCCESS: oldpost: {post}")
    print(f"HOOTSUITE:SUCCESS: newpost: {newpost}")
    return newpost, errors






##edge case for accesstoken not being used in a while?
def retoken(refreshtoken):
    """
   generates oauth token for hootsuite authentication

    Args:
        clientsecret, clientid, refreshtoken,

    Returns:
        accesstoken

      """
    encodedData = base64.b64encode(bytes(f"{client_id}:{client_secret}", "ISO-8859-1")).decode("ascii")
    print(refreshtoken)
    payload = {
        "grant_type": "refresh_token",
        "refresh_token": f"{refreshtoken}"
    }

    headers = {'Content-Type': 'application/x-www-form-urlencoded',
               'Authorization': f'Basic {encodedData}'}
    r = requests.post('https://platform.hootsuite.com/oauth2/token',data=payload, headers=headers)
    print(f'Hootsuite Status: {r.status_code}, Hootsuite Response: {r.text}')
    if r.status_code != 200:
        atoken = None
        rtoken = None
        errors = r.text
        return atoken, rtoken, errors
    else:
        dataa = r.json()
        errors = None
        atoken  = dataa["access_token"]
        rtoken = dataa["refresh_token"]
        print("old atoken: ", accesstoken)
        print("old rtoken: ",os.environ["refreshtoken"])  # outputs "value"
        os.environ["refreshtoken"] = rtoken
        os.environ["accesstoken"] = atoken
        print(f"NEW refresh {rtoken}")
        print("new refresh token: ",os.environ["refreshtoken"]) # outputs 'newvalue'
        print("new access token: ", atoken)

        errors = None
        print("refresh token repsone: ",r.text )

        # Write changes to .env file.
        d.set_key(env_file, "refreshtoken", os.environ["refreshtoken"])
        d.set_key(env_file, "accesstoken", os.environ["accesstoken"])
        return atoken # return id for later?

def hootsuite(post,at):
# url shortner?
    """
    Post to Twitter using Hoot Suite,
    Args:
        Post (str) - Social Media post

    Returns:
        Hootsuite ID (str) - Hootsuite Id to for social post
    """
    #fetch token
    #accesstoken = refreshtoken(refreshtoken)

    #add social profile ud to heroku environmental variable for easy changing
    payload = {
            "text": f'{post}',
            "socialProfileIds": [136495480], #Davis_shmavis,
            "scheduledSendTime": f'{utctimee}',
            "location": {"latitude": 34.56, "longitude": -12.34},
            "emailNotification": False
        }

    headers = {'Content-Type': 'application/json',
               'Authorization': f'Bearer {at}'}
    r = requests.post('https://platform.hootsuite.com/v1/messages',json=payload, headers=headers)
    print(f'Hootsuite Status: {r.status_code}, Hootsuite Response: {r.text}')

    if r.status_code != 200:
        data = None
        hootid = None
        errors = f"problem posting to hootsuite {r.text}"
        print(f"HOOTSUITE:ERROR: {r.text}")
        return data, errors, hootid
    else:
        data = r.json()
        hootid = data['data'][0]['id']
        errors = None
        print(f"HOOTSUITE:SUCCESS: HootSuite id: {hootid}, response: {r.text}")
        return data, errors, hootid


# def batchtitleid(listofIsbn):
#     """
#             #returns a list of valid titles and any title not found as errors
#
#             Args: listofIsbn (array) unqie identifier for the Title Object
#
#
#             Returns:
#
#     """
#
#      #input gets updated from param
#     print(listofIsbn)
#     payload =  {
#         "inputs": listofIsbn,
#         # "input" : f"{listofIsbn}",
#         "properties": ["title_name", "author"],
#         "idProperty": "isbnnumber"
#     }
#     url = f'https://api.hubapi.com/crm/v3/objects/Title/batch/read?hapikey={hapikey}'
#     headers = {"Content-Type": "application/json"}
#     res = requests.post(url, headers=headers, data=json.dumps(payload))
#     res = res.json
#     # title = res['results']
#     # author=
#     # id =
#     #log text or json response response
#     # print(res.text)
#     # will return a error if id not found so handle the errors, response is 200 if not, not sure about eith errors, add this error to the error list for the client and logg
#     return res
#


## change to use date provided in csv
def hsdate():
    """
    Used to put todays date into the correct format for hubspot

    Args - None
    Returns (datetime) - todays date

    """
    datetoday = datetime.today().strftime('%Y-%m-%d')
    return datetoday

#reformat to include any additional titles, authors and promo art - see update promo in ayrshare.py
#test using empty fields
#add time use hsdate()
def createpromo(x, hootid, newpost, title1, author):
    """
    Creates promotion record in Hubspot

    Args:
        postplatform, postdate, promotype, publisher, ayrshareid, promolandingpageurl,title,author,email promo url1, social post, endate, discount amount, email form name, email from user, Ref id
        all args come directly from the CSV uploaded by client
        Ref id : unique identifier

    Returns:
        promoid int: Promotion Record ID
    """
    refid = x["Ref ID"]
    from_name = x['Email From Name']
    from_user = x["Email From User"]
    platform = x["Platform"]
    publisher = x['Publisher']
    promotype = x['Promotion Type']
    promourl = x['Promo Landing Page URL']
    url1 = x['Email promotion cover art URL 1']
    end = x['End Date']
    discount = x['Discount Percent']
    datetoday = hsdate()



    url = f"https://api.hubapi.com/crm/v3/objects/Promotion?hapikey={hapikey}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "properties": {
            'title1': title1,
            'author': author,
            # 'ref_id_': refid,
            'name': f'Post + Tag - {title1}',
            # 'scheduled_post_time': datetoday,
            'promotion_distribution_method':'post_and_tag',
            'from_name': from_name,
            'from_user': from_user,
            'platform': platform,
            'publisher': publisher,
            'promotion_type': promotype,
            'hootsuite_id': hootid,
            'promo_landing_page_url': promourl,
            'email_promotion_cover_art_url': url1,
            'social_media_message': newpost,
            'enddate': end,
            'discount_percent': discount,
            }
        }
    res = requests.post(url, headers=headers, data=json.dumps(payload))
    if res.status_code != 201:
        print(f"HOOTSUITE:ERROR: Error creating promotion record{res.text}")
        # logger.error(f"HOOTSUITE:ERROR: Error creating promotion record{res.text}")
        return None
    else:
        r = res.json()
        promoid = r['id']
        print(f"HOOTSUITE:SUCCESS: Promo created: {res.text}")
        # logger.debug(f"HOOTSUITE:SUCCESS: Promo created {res.text}")
        return promoid


def batchassociate(payload,object):
    """
        Associates The Promotion Object to The Title Object and it related Companies and Contacts.

        Args:


        Returns:

    """
    ##example payload
#     payload = {
#         #update input with param
#     "inputs":[
#         {
#             "from":{"id":"66547651"},
#             "to":{"id":"8309675839"},
#             "type":"contact_to_company"
#         },
#         {
#             "from":{"id":"66547701"},
#             "to":{"id":"8309675839"},
#             "type":"contact_to_company"
#         }
#     ]
# }
    url = f'https://api.hubapi.com/crm/v3/associations/Promotion/{object}/batch/create?hapikey={hapikey}'
    headers = {"Content-Type": "application/json"}
    res = requests.post(url, headers=headers, json=payload)
    print(f"HOOTSUITE:SUCCESS: Batch {object} associations: {res.text}")
    return res

def parsecsv(csv, at):
    """
    Loops thru a csv uploaded to flask app.
    Creates a payload for Hootsuite API using Hubspot data and from the CSV.
    This functions creates a Hootsuite post and A Promotion Record in HubSpot.

    Arg:
        csv (dictionary) - uploaded thru flask app

    Return:
        hsassociations (list of dictionaries) - a list of title id's, contacts id's and promo id's
        client csv (dictionary) - csv of user errrors for client
    """
    clientcsv = []
    associations = []
    for x in csv:
        platform = x['Platform']
        #split here by platform, followed by else for email logic
        #if platform != Email....else

        hubspotids = {}

        #for client csv
        x['errors'] = ''
        x['title1'] = ''

        print(f"HOOTSUITE:STATUS: Searching for ISBN")
        isbn1 = x["ISBN # - 1"]
        titleid, errors, title1, author = gettitleid1(isbn1)

        #for client csv
        if errors:
            x['errors'] = f'ISBN Errors: {errors}'
            # clientcsv.append(errors)

        #for client error csv
        if title1:
            x['title'] = title1


        if not titleid:
            continue
        print(f"HOOTSUITE:STATUS: Searching for contacts related to title")
        hubspotids["titleid"] = titleid
        contactids = titlecon2(titleid)

        if not contactids:
            continue
        print(f"HOOTSUITE:STATUS: Formatting Post")
        hubspotids["contactids"] = contactids
        newpost, errors = formatpost(x, contactids, title1)

        if errors:
            # for client error csv
            x['errors'] = f'contact Errors: {errors}'
            # clientcsv.append(errors)

        if not newpost:
            continue

        data, errors, hootid = hootsuite(newpost, at)

        # for client error csv
        if errors:
            x['errors'] = f'Hootsuite Errors: {errors}'
            # clientcsv.append(errors)
            print(f'Hootsuite Errors: {errors}')

        if not hootid:
            continue

        promoid = createpromo(x, hootid, newpost, title1, utctimee)
        if not promoid:
            continue

        hubspotids["promoid"] = promoid

        associations.append(hubspotids)

        clientcsv.append(x)
    return clientcsv, associations


def hsassociations(associations):
    """
    Batch Associated Title and Contact to promotion

    Arg (list) - A list of dictionaries containing Titleid, ContactID and PromoID

    Response - StatusCode
    """
    print((f"HOOTSUITE:STATUS: Associating {associations}"))

    # create title batch list
    titlebatch = []
    for x in associations:
        tid = x['tid']
        pid = x['pid']

        tbatch = {
            "from": {"id": pid},
            "to": {"id": tid},
            "type": "promotion_to_title"
        }
        titlebatch.append(tbatch)

    payload1 = dict({"inputs": titlebatch})
    object = "Title"
    # associate
    batchassociate(payload1, object)

    # batch contact list
    contactbatch = []
    for x in data:
        pid = x["pid"]
        cid = x['cid']
        if cid:
            for x in cid:
                conid = x['id']

                cbatch = {
                    "from": {"id": pid},
                    "to": {"id": conid},
                    "type": "promotion_to_contact"
                }
                contactbatch.append(cbatch)

    payload2 = dict({"inputs": contactbatch})
    object = "Contact"
    batchassociate(payload2, object)

testcsv = [{"ISBN # - 1": "9781541477087","Social Media Message":" @ (title) (end)","Ref ID":"55","ISBN # - 2": "", "ISBN # - 3": "", "ISBN # - 4": "", "Promotion Type": "",
            "Publisher": "", "Promo Landing Page URL": "", "Schedule Post Date": "", "Scheduled Post Time": "",
            "Email From Name": "", "Email From User": "", "Email promotion cover art URL 1": "",
            "Email promotion cover art URL 2": "", "Email promotion cover art URL 3": "", "End Date": "2022-04-04",
            "Discount Percent": "", "Platform": "Twitter"},
           {"ISBN # - 1": "9781490662336","Social Media Message":"@ (title) (end)", "Ref ID":"65","ISBN # - 2": "", "ISBN # - 3": "", "ISBN # - 4": "", "Promotion Type": "",
            "Publisher": "", "Promo Landing Page URL": "", "Schedule Post Date": "", "Scheduled Post Time": "",
            "Email From Name": "", "Email From User": "", "Email promotion cover art URL 1": "",
            "Email promotion cover art URL 2": "", "Email promotion cover art URL 3": "", "End Date": "2022-04-04",
            "Discount Percent": "", "Platform": "Twitter"},
           {"ISBN # - 1": "2","Social Media Message":"@ (title) (end)", "Ref ID":"","ISBN # - 2": "", "ISBN # - 3": "", "ISBN # - 4": "", "Promotion Type": "",
            "Publisher": "", "Promo Landing Page URL": "", "Schedule Post Date": "", "Scheduled Post Time": "",
            "Email From Name": "", "Email From User": "", "Email promotion cover art URL 1": "",
            "Email promotion cover art URL 2": "", "Email promotion cover art URL 3": "", "End Date": "2022-04-04",
            "Discount Percent": "", "Platform": "Twitter"}]

def main(csv):
    print(f"HOOTSUITE:STATUS: Starting Script...")
    at = retoken(refreshtoken)
    clientcsv, associations = parsecsv(csv,at)
    # hsassociations(associations)
    # WriteToS3(clientcsv)


    #### dont look at me, i'm for testing ####
    # print(f"HOOTSUITE:STATUS: client csv {clientcsv})
    # print(f"HOOTSUITE:STATUS: association list {associations})
    # print(f"HOOTSUITE:STATUS: Hubspot to associate list {hsassociations}")

main(testcsv)





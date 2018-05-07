
import json
import urllib.request
import time
import numpy as np
import matplotlib.pyplot as plt
import math
import facebook
import pandas as pd


accessToken = ''

beginDate = '1462060800'
endDate = '1478649599'


def apiCall(strCall):
    
    htmlFile = urllib.request.urlopen(strCall)
    htmlText = htmlFile.read()
    
    return json.loads(htmlText)

def getPosts(strNewsID):
    allPosts = []
    apiURL =  'https://graph.facebook.com/v2.6/' + strNewsID + '/feed?until=1478649599&since=1462060800&access_token=' + accessToken
    
    newsPosts = apiCall(apiURL)
    allPosts.append(newsPosts)
    
    nextPostData = newsPosts.get('paging').get('next')
    allPosts = iteratePage(allPosts, nextPostData)
    
    
    #flatten nested dictionaries to single dimensional array of posts
    flattenedPosts = []
    for i in allPosts:
        print(type(i))
        for j in i.get('data'):
            # For each posts, add reactions to the dictionary of the post
            print('adding react data to post: ' + j.get('id'))
            j = {**j,**addReacts(j.get('id'))}
            
            # Replace 25 limited comments with full comment, but keep total_comment variable availalbe
            j['totalComments'] = j.get('comments').get('summary').get('total_count')
            j['comments'] = getComments(j.get('id'))
            
            flattenedPosts.append(j)
    return flattenedPosts

def getComments(strPostID):
    allComments = []
    apiURL = 'https://graph.facebook.com/v2.6/' + strPostID + '/?fields=comments.limit(500)&access_token=' + accessToken
    print('Getting Comment Data for: ' + strPostID)
    commentPosts = apiCall(apiURL)
    
    allComments.append(commentPosts)
    
    
    nextComPage = commentPosts.get('paging')
    
    if nextComPage is not None:
        nextComData = commentPosts.get('paging').get('next')
        allComments = iteratePage(allComments, nextComData)
    
    
    flattenedComments = []
    
    for i in allComments:
        #For Each Comment Page
        for j in i.get('comments').get('data'):
            #For Each comment in a comment page (Limit 500 per comment page)
            flattenedComments.append(j)
    
    return flattenedComments
    
    

def iteratePage(pageList, strNextCall):
    
    newsPage = apiCall(strNextCall)
    
    pageList.append(newsPage)    
    #Iterate through pages
    nextPage = newsPage.get('paging')
    if nextPage is not None:
        nextPostData = nextPage.get('next')
        pageList = iteratePage(pageList,nextPostData)
    else:
        return pageList
    
    return pageList



def addReacts(postID):
    ## Setup Reacts for API Calls
    reacts = ['NONE', 'LIKE', 'LOVE', 'WOW', 'HAHA', 'SAD', 'ANGRY', 'THANKFUL', 'PRIDE']

    summaryReactInfo = ""
    for x in reacts:
        summaryReactInfo += "reactions.type(" + x + ").limit(100).summary(total_count).as(reactions_" + x + "),"
        
    allReacts = summaryReactInfo + 'shares,comments.summary(true),likes'
    
    #Call for reacts
    graph = facebook.GraphAPI(access_token=accessToken)
    allReacts = summaryReactInfo + 'shares,comments.summary(true), likes'

    #POST DATA WITH REACTS
    postData = graph.get_object(id = postID, fields = allReacts)

    return postData                                                                                                                                                             

def postsToCSV(postList, strNewsID):
    
    #create empty lists to eventually move to dataframe
    
    message = []
    created_time = []
    postID = []
    NONE_reaction = []
    LIKE_reaction = []
    LOVE_reaction = []
    WOW_reaction = []
    HAHA_reaction = []
    SAD_reaction = []
    ANGRY_reaction = []
    THANKFUL_reaction = []
    PRIDE_reaction = []
    totalShares = []
    totalComments = []
    #Create empty fields for comments file
    comPostID = []
    commenterID = []
    comMessage = []
    comCreatedTime = []
    
    
    for x in postList:
        
        message.append(x.get('message'))
        created_time.append(x.get('created_time'))
        postID.append(x.get('id'))
        NONE_reaction.append(x.get('reactions_NONE').get('summary').get('total_count'))
        LIKE_reaction.append(x.get('reactions_LIKE').get('summary').get('total_count'))
        LOVE_reaction.append(x.get('reactions_LOVE').get('summary').get('total_count'))
        WOW_reaction.append(x.get('reactions_WOW').get('summary').get('total_count'))
        HAHA_reaction.append(x.get('reactions_HAHA').get('summary').get('total_count'))
        SAD_reaction.append(x.get('reactions_SAD').get('summary').get('total_count'))
        ANGRY_reaction.append(x.get('reactions_ANGRY').get('summary').get('total_count'))
        THANKFUL_reaction.append(x.get('reactions_THANKFUL').get('summary').get('total_count'))
        PRIDE_reaction.append(x.get('reactions_PRIDE').get('summary').get('total_count'))
        totalShares.append(x.get('shares').get('count'))
        totalComments.append(x.get('totalComments'))
        for j in x.get('comments'):
            comPostID.append(x.get('id'))
            commenterID.append(j.get(''))
            comMessage.append(j.get('message'))
            comCreatedTime.append(j.get('created_time'))
    
    #Posts Dataframe
    
    postDF = pd.DataFrame({'postID':postID, 'message': message, 
                          'created_time' : created_time, 'NONE_reaction' : NONE_reaction,
                          'LIKE_reaction' : LIKE_reaction, 'LOVE_REACTION' : LOVE_reaction,
                          'WOW_reaction' : WOW_reaction, 'HAHA_reaction' : HAHA_reaction,
                          'SAD_reaction' : SAD_reaction, 'ANGRY_reaction' : ANGRY_reaction,
                          'THANKFUL_reaction' : THANKFUL_reaction, 'PRIDE_reaction' : PRIDE_reaction,
                          'total_shares' : totalShares, 'totalComments' : totalComments})
    
    #Commends DataFrame
    commentsDF = pd.DataFrame({'postID' : comPostID, 'commenterID' : commenterID,
                              'comMessage' : comMessage, 'comCreatedTime' : comCreatedTime})
    
    
    postFN = strNewsID + '_POSTS.CSV'
    commentsFN = strNewsID + '_COMMENTS.CSV'
    
    postDF.to_csv(postFN)
    commentsDF.to_csv(commentsFN)
    
    return
    


bbcNewsID = '228735667216'
cnnID = '5550296508'

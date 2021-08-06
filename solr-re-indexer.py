"""
Purpose:
    Takes a source server, target server, and collection. The script will query the source and target
    servers for their leader cores of the collection, and then it will replicate the source collection
    onto the target collection.

Note:
In the newer python request package (urllib3) HTTPS connections are verified by default (cert_reqs = 'CERT_REQUIRED')
We need to supply the Aries certificate chain to avoid the following warning in the console:
  "InsecureRequestWarning: Unverified HTTPS request is being made to host 'xxx'. Adding certificate verification is strongly advised"
"""

import sys, requests, getopt, math
from requests.auth import HTTPBasicAuth
from tqdm import tqdm


# Location of the certificates
pathToSourceServerCert = "cert/source_server.crt"
pathToTargetServerCert = "cert/target_server.crt"

# Main Function
def main(parameters):
    srcServer = ''
    tgtServer = ''
    solrCollection = ''
    solrUser = ''
    solrPass = ''
    isVerbose = False
    batchSize = 1000

    # Parses the arguments and returns a key and value arrays.
    try:
        opts, args = getopt.getopt(parameters, "hs:t:c:u:p:b:v",
                                   ["source=", "target=", "collection=", "username=", "password=", "batchSize=", "verbose="])
    # Error if unable to parse.
    except getopt.GetoptError:
        # Print a friendly message to the user.
        print(
            'ess-re-indexer.py -s <source server> -t <target server> -c <Solr collection> -u <Solr username> -p <Solr password> -b <batch size>')
        # Abnormally exit.
        sys.exit(2)
    # Loop through the parsed arguments.
    for opt, arg in opts:
        if opt == '-h':
            print(
                'ess-re-indexer.py -s <source server> -t <target server> -c <Solr collection> -u <Solr username> -p <Solr password> -b <batch size>')
            sys.exit()
        elif opt in ("-s", "--source"):
            srcServer = arg
        elif opt in ("-t", "--target"):
            tgtServer = arg
        elif opt in ("-c", "--collection"):
            solrCollection = arg
        elif opt in ("-u", "--username"):
            solrUser = arg
        elif opt in ("-p", "--password"):
            solrPass = arg
        elif opt in ("-b", "--batchSize"):
            batchSize = int(arg)
        elif opt in ("-v", "--verbose"):
            isVerbose = True

    # Check if the collection is an empty string.
    if not solrCollection:
        # Print a friendly message to the user.
        print('ERROR: No Solr collection was provided!')
        # Exit abnormally.
        sys.exit(3)
    else:
        # Check if the target server is an empty string.
        if not tgtServer:
            # Print a friendly message to the user.
            print('ERROR: No Target Solr server was provided!')
            # Exit abnormally.
            sys.exit(4)
        else:
            # Check if the source server is an empty string.
            if not srcServer:
                # Print a friendly message to the user.
                print('ERROR: No Source Solr server was provided!')
                # Exit abnormally
                sys.exit(5)
                # Username and Password may be empty due to no authentication.

    # Let's ask if we need to use HTTPS.
    answer = input('Do we need to use HTTPS for ' + srcServer + '? (Y/N) ')
    # Let's look at their answer. Was it a yes?
    if answer.lower() == 'y':
        # Let's adjust the source server to use HTTPS.
        srcServer = "https://" + srcServer
    else:
        # Let's adjust the source server to use HTTP.
        srcServer = "http://" + srcServer
    # print(srcServer)
    # Let's ask if we need to use HTTPS for the target server.
    answer = input('Do we need to use HTTPS for ' + tgtServer + '? (Y/N) ')
    # Let's look at their answer. Was it a yes?
    if answer.lower() == 'y':
        # Let's adjust the target server to use HTTPS.
        tgtServer = "https://" + tgtServer
    else:
        # Let's adjust the target server to use HTTP.
        tgtServer = "http://" + tgtServer

    # Create the url string.
    solr = srcServer + "/solr/" + solrCollection + "/select?q=*&rows=0&distrib=false"

    # Check if the username is empty.
    if not solrUser:
        # Send the request.
        results = requests.get(url=solr)
    else:
        # Send the request.
        results = requests.get(url=solr, auth=HTTPBasicAuth(solrUser, solrPass), verify=pathToSourceServerCert)

    # Grab the number of documents in the collections.
    docCount = results.json()['response']['numFound']

    # Check if the number of documents in the collection is divisible by the batch number
    isDivisible = True if docCount % batchSize == 0 else False

    # Calculate how many iterations do we need
    iteration = int(docCount/batchSize) if isDivisible else math.ceil(docCount/batchSize)

    # Print job information
    print('\tCollection name: ', solrCollection)
    print('\tTotal document count: ', docCount)
    print('\tBatch size: ' + str(batchSize))
    print('\tNumber of batches: ' + str(iteration))
    print('Start re-indexing...')

    for i in tqdm(range(iteration), desc = "Documents processed"):
        # Start doc number
        start = i * batchSize
        # number of docs in this iteration
        rows = batchSize if (isDivisible and i < iteration) or (not isDivisible and i < iteration - 1) else docCount % batchSize
        # all the documents in this batch
        batchDocs = []

        # Create the url string, retrieving the specific document.
        getSolr = srcServer + "/solr/" + solrCollection + "/select?q=*&rows=" + str(rows) + "&start=" + str(start) + "&distrib=false&fl=*"

        # Check if the username is empty.
        if not solrUser:
            # Send the request.
            results = requests.get(url=getSolr)
        else:
            # Send the request.
            results = requests.get(url=getSolr, auth=HTTPBasicAuth(solrUser, solrPass), verify=pathToSourceServerCert)

        # Remove unnecessary LucidWorksFusion fields
        for j in range(rows):
            docJson = results.json()['response']['docs'][j]

            keys = tuple(docJson.keys())

            # Loop through the document.
            for key in keys:
                # Check if the key starts with an underscore.
                if key.startswith('_'):
                    # If it does, remove it.
                    del docJson[key]

            # append to the batch
            batchDocs.append(docJson)

        # Print json data sent to target Solr
        if isVerbose:
            print(batchDocs)

        # Create the url string, retrieving the specific document.
        postSolr = tgtServer + "/solr/" + solrCollection + "/update?commit=true&wt=json"

        # Create the url string, retrieving the specific document.
        postSolr = tgtServer + "/solr/" + solrCollection + "/update?commit=true&wt=json"

        # Check if the username is empty.
        if not solrUser:
            # Send the data.
            results = requests.post(url=postSolr, headers={"content-type": "application/json"}, json=batchDocs)
        else:
            # Send the data.
            results = requests.post(url=postSolr, auth=HTTPBasicAuth(solrUser, solrPass), verify=pathToTargetServerCert, json=batchDocs)

# Run the main function, passing the arguments with it.
if __name__ == "__main__":
    main(sys.argv[1:])

from rmapy.api import Client as Client
import rmapy.api
import helpers
from rmapy.document import ZipDocument as ZipDocument


class paperKid(object):
    """
    Handles uploading file to Remarkable API
    """
    def __init__(self,filename):
        self.filename = filename

    def getAuth(self,tokenValue):
        """
        Confirm auth with the remarkable
        """
        rmapyObject = Client()
        if not rmapyObject.is_auth():
            helpers.debug("Needing new auth token")
            rmapyObject.register_device(tokenValue)
            rmapyObject.renew_token()
        else:
            helpers.debug("Already auth'd good to go")
            return True
        if rmapyObject.is_auth():
            helpers.ok("Been able to get auth")
            return True
        else:
            helpers.err("Something went wrong with auth")
            return False


    def yeetPaper(self):
        """
        Attempt to upload the file to the remarkable servers
        """
        helpers.debug("Start the yeet")
        rm = Client()
        if rm.renew_token():
            helpers.debug("Token OK uploading file " + self.filename)
            rawDocument = ZipDocument(doc=self.filename)
            helpers.debug(rawDocument.metadata["VissibleName"])
            helpers.debug(str(rawDocument))
            books = [i for i in rm.get_meta_items() if i.VissibleName == "Newspaper"][0]
            rm.upload(rawDocument, books)
            collection = rm.get_meta_items()
            if [ i.VissibleName for i in collection.children(books) if i.Type == "DocumentType" ]:
                helpers.debug("Sent a new file")
            else:
                helpers.err("File not in the API!")
        else:
            helpers.err("Unable to talk to the API : Session rotate")

PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;

-- Much of this isnt used yet, allowing room to build out features
CREATE Table Sources(
   sourceID INTEGER PRIMARY KEY,
   name TEXT,   -- Name of the source
   Attr TEXT,   -- Default author if we are unable to enrich
   cType TEXT,  -- processor type
   sType Text,  -- Sub type
   Weight INT, -- Default weight
   cMax  INT, -- Max number of things
   URL TEXT UNIQUE, -- URL to source
   repeat int, -- Do we want to allow repeated things
   noSum int  -- Do we want to disable stemmer?
);

INSERT INTO Sources VALUES (NULL,'RedditNetSecNew','Unkown Reddit User','json','reddit',0.7,15,'https://reddit.com/r/netsec/new/.json',0,0);
INSERT INTO Sources VALUES (NULL,'RedditWorldNewsNew','Unkown Reddit User','json','reddit',0.7,15,'https://reddit.com/r/worldnews/new/.json',0,0);
INSERT INTO Sources VALUES (NULL,'RedditUkNewsNew','Unkown Reddit User','json','reddit',0.7,5,'https://reddit.com/r/uknews/new/.json',0,0);
INSERT INTO Sources VALUES (NULL,'RedditScienceNewsNew','Unkown Reddit User','json','reddit',0.7,10,'https://reddit.com/r/science/new/.json',0,0);
INSERT INTO Sources VALUES (NULL,'RedditinthenewsNew','Unkown Reddit User','json','reddit',0.7,5,'https://reddit.com/r/inthenews/new/.json',0,0);
INSERT INTO Sources VALUES (NULL,'RedditReNew','Unkown Reddit User','json','reddit',0.7,15,'https://reddit.com/r/ReverseEngineering/new/.json',0,0);


CREATE TABLE SourceExceptions(
   sourceID INTEGER PRIMARY KEY,
   name TEXT,   -- Name of the exception
   URL TEXT UNIQUE, -- URL to exception
   anchor TEXT UNIQUE, -- Regex of the url to blacklist
   reason TEXT UNIQUE -- Whats differnt? (IE if its a tube vid we need to use the subs)
);

CREATE TABLE History(
   newsID INTEGER PRIMARY KEY,
   source TEXT, -- THis should be an ID to link Sources and History
   Author TEXT,
   Title TEXT,
   URL TEXT UNIQUE,
   permURL TEXT UNIQUE,
   published BOOL,
   datePublished DATE,
   weight INT, -- Take the programs assigned weight or fall to default
   summary TEXT,
   borked DATE,
   sourceID INT,
   authToken TEXT,
   shortURL TEXT
);

CREATE Table Stats(
   paperID INTEGER PRIMARY KEY,
   issue int,
   pages int
);

COMMIT;

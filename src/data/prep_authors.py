import pandas as pd


# get authorship information from raw dataframe WITH all other data
def get_authors(df_input): # input: articles after get_dict_info
    # create empty dataframe with all authorship attributes
    df = pd.DataFrame()
    authors_list = []
    
    for article in df_input.itertuples():
        authors = pd.DataFrame(article.authorships)
        
        if len(authors) != 0:
            # disassemble author info
            for author in authors.itertuples():
                new_info = [article.id]+[author.author_position]+list(author.author.values())+[author.raw_affiliation_string]
                
                # add institution info
                if len(author.institutions) != 0:
                    new_info += list(author.institutions[0].values()) 
                else:
                    # no institution, no info
                    new_info += [None, None, None, None, None]
                authors_list.append(new_info) 
    
    new_df = pd.DataFrame(authors_list, 
                          columns=["article_id", "author_position", "author_id", "author_display_name", "orcid",
                                   "raw_affiliation_string", 
                                   "inst_id", "inst_display_name", "ror", "inst_country_code", "inst_type"])
    df = pd.concat([df, new_df])
    
    return pd.merge(df, df_input, left_on="article_id", right_on="id")


# keep most recent publication per author
def get_single_authors(df_input): # input: authors with doubles
    keep = []
    
    for author in set(df_input["author_id"]):
        # get all rows that match author
        publications = df_input[df_input["author_id"]==author]
        # get most recent one
        most_recent = publications["publication_date"].max()
        keep += publications[publications["publication_date"]==most_recent].values.tolist()
    
    keep_df = pd.DataFrame(keep,
                           columns = df_input.columns)
    
    # drop duplicates because some articles may have been found twice through different queries 
    # and some authors have published multiple relevant articles on the same day
    return keep_df.drop_duplicates(subset=["author_id"])


# filter a list of authors for authors who are asscociated with at least one European institution
def get_eu_authors(df_input): # input: authors
    keep = []
    eu_codes = ["IS", "SV", "FO", "NO", "FI", "SE", "DK", # Nordic
                "EE", "LV", "LT", # Baltic 
                "IE", "IM", "GB", "GI", # Great Britain
                "NL", "BE", "LU", # Benelux
                "ES", "PT", "MT", "FR", "IT", "GR", # Mediterranean
                "BA", "HR", "SI", "ME", "RS", "MK", "AL", # Balkan
                "DE", "CZ", "CH", "AT", "SK", "PL", "HU", # Central
                "BY", "UA", "MD", "RO", "BG" # Eastern
                "SM", "VA", "LI", "AD", "MC"] # Micronations

    for author in df_input.itertuples():
        # check every affiliated institute
        if author.inst_country_code in eu_codes:
            keep.append(author)
    
    return pd.DataFrame(keep)

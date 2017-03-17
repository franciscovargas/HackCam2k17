# HackCam2k17 (VERTEX)

This repo contains a web application that wraps around a Bing scrapper Sampler, presented in a force directed GUI graph approach. We named the application Vertex.

## Sampling and Scraping Bing 

We have built a scraper on top of the bing API that given a query passed via the front end we return a non biased randomised search over bings results.

Lets say we return a number of K results. Out of those K results a number \alpaha (set apriori as \approx 1). We sample randomly from the top 50 ranked bing results K*\alpha*2^-1 then in th range (50,100] we sample K* alpha * 2^-2  then in the range (100, 150] K* alpha * 2^-3 untill the decay factor 2^-n becomes negligible.  

This procedure gives us a set of K urls namely X. We then scrape the text content of the X urls combining both NLTK and a hashset of the english dictionary. This is a timely procedure which is currently under optmisation using pool from multiprocessing. After the text is extracted this is extracted we perform stemming to remove word morphologies  and T-IDF genrating the design Matrix \Phi where each row corresponds to a sparse matrix representation of the text in each url.

Currently the K is set to 35, where 10 pages are sampled from the first 20 results, 15 pages are sampled from the results 20 to 100 and 10 pages are sampled from the results 100 to 150.

## Force Directed Graph

Rather than constructing the usual network where the edges reprent hyperlinks coming out of the node (urls) we create edges and weights on those edges based on the correlation of the text between text in url1 and text in url2. For this we use the cosine similarity measure asisted via the TF-IDF repr. If correlation is two low there is now edge , if its above that threshold there is an edge with a pulling force between the two nodes. D3 was used to animate the force graph.

## Taxonomy Clustering on The Graph

Once the graph G(V,E) was generated we decided to carry out clustering to group the search results in order to place similar topics together and aid the user in discovery.  To do this we assumed that the number of cluster C is latent and we infer it by minimising the second derivative (discrete approximation) of the intra cluster aggregate distance (also known as the elbow method). We then used these results to color the nodes in our graph, nicely the coulouring also matched the spectral clustering automatically performed by the force directed graph d3js backend.

## Screenshot
![alt tag](https://github.com/franciscovargas/HackCam2k17/raw/master/Screenshot1.png)
Results for query "smartphone"
 

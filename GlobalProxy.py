#! /usr/bin/python

from multiprocessing import Process, Pool, cpu_count
from multiprocessing.pool import ApplyResult
import os, re, random, urllib, urllib2, cookielib, sys, BeautifulSoup

class Proxy:
  
  def UserAgent ( self ):
    agents = [
      'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:25.0) Gecko/20100101 Firefox/25.0',
      'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:25.0) Gecko/20100101 Firefox/25.0',
      'Mozilla/5.0 (Windows NT 6.0; WOW64; rv:24.0) Gecko/20100101 Firefox/24.0',
      'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:24.0) Gecko/20100101 Firefox/24.0',
      'Mozilla/5.0 (Windows NT 6.2; rv:22.0) Gecko/20130405 Firefox/23.0',
      'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20130406 Firefox/23.0',
      'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:23.0) Gecko/20131011 Firefox/23.0',
      'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:21.0) Gecko/20130331 Firefox/21.0',
      'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:21.0) Gecko/20100101 Firefox/21.0',
      'Mozilla/5.0 (X11; Linux i686; rv:21.0) Gecko/20100101 Firefox/21.0',
      'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
      'Googlebot/2.1 (+http://www.googlebot.com/bot.html)',
      'Googlebot/2.1 (+http://www.google.com/bot.html)',
      'Mozilla/5.0 (compatible; MSIE 10.6; Windows NT 6.1; Trident/5.0; InfoPath.2; SLCC1; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; .NET CLR 2.0.50727) 3gpp-gba UNTRUSTED/1.0',
      'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0)',
      'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/6.0)',
      'Mozilla/5.0 (Windows; U; MSIE 9.0; WIndows NT 9.0; en-US))',
      'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0; chromeframe/13.0.782.215)',
      'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.0; Trident/4.0; GTB7.4; InfoPath.3; SV1; .NET CLR 3.1.76908; WOW64; en-US)'
      ]
    return agents[ random.randrange(0, len(agents) ) ]
  
  
  def Connection ( self, uri, proxy = None ):
    cj = cookielib.CookieJar()
    
    if ( proxy ):
      proxy_handler = urllib2.ProxyHandler({ 'http' : 'http://' + proxy })
      url = urllib2.build_opener( proxy_handler, urllib2.HTTPCookieProcessor( cj ), urllib2.HTTPHandler( debuglevel = 0 ) )
    else:
      url = urllib2.build_opener( urllib2.HTTPCookieProcessor( cj ), urllib2.HTTPHandler( debuglevel = 0 ) )
 
    urllib2.install_opener( url )
    headers = { 'User-Agent' : self.UserAgent, }
    url = urllib2.Request( uri, None, headers )
    
    try:
      url = urllib2.urlopen( url, timeout = 5 )
      return url.read()
    except:
      return
  
  
  def Pages ( self, FootPrint ):
    GET = urllib.urlencode( { 'hl' : 'en', 'q' : FootPrint, 'num' : 100, 'as_qdr' : 'all' } )
    html = BeautifulSoup.BeautifulSoup( self.Connection( 'http://www.google.com/search?%s' % ( GET ) ) )
    try:
      link = []
      for a in html.findAll('a'):
	if re.search( 'google', a['href'] ):
	  pass
	else:
	  link.append( a['href'].replace('/url?q=','').split('&sa')[0] )
      return self.ArrayUnique( link )
    except:
      pass
  
  
  def IP ( self, Page ):
    try:
      proxy = []
      html = self.Connection( Page )
      proxies = re.findall( '\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\:\d{1,4}', html )
      #print proxies
      #for ip in proxies:
      # if self.Connection( "http://www.google.com/", ip ):
	  #print ip
	  #proxy.append( ip )
      return self.ArrayUnique( proxies )
    except:
      pass
  
  
  def ArrayUnique ( self, array ):
    unique = []
    for item in array:
      if item not in unique:
	unique.append( item )
    return unique


class Manage:
  
  def __init__ ( self, cin ):
    self.Proxy = Proxy()
    
    pool = Pool( processes = cpu_count() )
    
    if ( cin == "pages" ):
      FootPrints = [ '+":80" +":8080" +":3128"','inurl:proxy +8080','+":80" +":8080" +":3128" +"socks"','+":80" +":8080" +":3128" +"socks" +"pl"']
      opFile = 'ProxyPageList.txt'
      async_results = [ pool.apply_async( self, ( cin, fp, ) ) for fp in FootPrints ]
    elif ( cin == "ip" ):
      pages = 'ProxyPageList.txt'
      opFile = 'ProxyList_1.txt'
      pages = open( pages, 'r' ).read().split( '\n' )
      async_results = [ pool.apply_async( self, ( cin, page, ) ) for page in pages ]
     
    pool.close()
    pool.join()
    
    try:
      os.remove( opFile )
    except:
      pass
  
    map( ApplyResult.wait, async_results )
    ar_results = [ ar.get() for ar in async_results ]
    try:
      f = open( opFile, 'a' )
      for results in ar_results:
	for result in results:
	  if re.search( 'google' , result ):
	    pass
	  elif re.search ( 'http' , result ):
	    f.write( result + '\n' )
	  elif re.findall( '\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\:\d{1,4}', result ):
	    f.write( result + '\n' )
      f.close()
    except:
      pass
  

  def __call__ ( self, cin, items ):
    if ( cin == "pages" ):
      return self.Pages( items )
    elif ( cin == "ip" ):
      return self.IP( items )
  
  
  def Pages ( self, FootPrints ):
    return self.Proxy.Pages( FootPrints )
    
    
  def IP ( self, Page ):
    return self.Proxy.IP( Page )


if __name__ == '__main__':
  Manage = Manage( sys.argv[1] )
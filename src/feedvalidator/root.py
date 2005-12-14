"""$Id$"""

__author__ = "Sam Ruby <http://intertwingly.net/> and Mark Pilgrim <http://diveintomark.org/>"
__version__ = "$Revision$"
__date__ = "$Date$"
__copyright__ = "Copyright (c) 2002 Sam Ruby and Mark Pilgrim"
__license__ = "Python"

from base import validatorBase

rss11_namespace='http://purl.org/net/rss1.1#'
purl1_namespace='http://purl.org/rss/1.0/'
soap_namespace='http://feeds.archive.org/validator/'
pie_namespace='http://purl.org/atom/ns#'
atom_namespace='http://www.w3.org/2005/Atom'

#
# Main document.  
# Supports rss, rdf, pie, and ffkar
#
class root(validatorBase):

  def __init__(self, parent, base):
    validatorBase.__init__(self)
    self.parent = parent
    self.dispatcher = parent
    self.name = "root"
    self.xmlBase = base
    self.xmlLang = None

  def startElementNS(self, name, qname, attrs):
    if name=='rss':
      if qname:
        from logging import InvalidNamespace
        self.log(InvalidNamespace({"parent":"root", "element":name, "namespace":qname}))
        validatorBase.defaultNamespaces.append(qname)

    if name=='feed' or name=='entry':
      if qname==pie_namespace:
        from logging import ObsoleteNamespace
        self.log(ObsoleteNamespace({"element":"feed"}))
        validatorBase.defaultNamespaces.append(pie_namespace)
        from logging import TYPE_ATOM
        self.setFeedType(TYPE_ATOM)
      elif not qname:
        from logging import MissingNamespace
        self.log(MissingNamespace({"parent":"root", "element":name}))
      else:
        from logging import TYPE_ATOM
        self.setFeedType(TYPE_ATOM)
        validatorBase.defaultNamespaces.append(atom_namespace)
        if qname<>atom_namespace:
          from logging import InvalidNamespace
          self.log(InvalidNamespace({"parent":"root", "element":name, "namespace":qname}))
          validatorBase.defaultNamespaces.append(qname)

    if name=='Channel':
      if not qname:
        from logging import MissingNamespace
        self.log(MissingNamespace({"parent":"root", "element":name}))
      elif qname != rss11_namespace :
        from logging import InvalidNamespace
        self.log(InvalidNamespace({"parent":"root", "element":name, "namespace":qname}))
      else:
        validatorBase.defaultNamespaces.append(qname)
        from logging import TYPE_RSS1
        self.setFeedType(TYPE_RSS1)

    validatorBase.startElementNS(self, name, qname, attrs)

  def unknown_starttag(self, name, qname, attrs):
    from logging import ObsoleteNamespace,InvalidNamespace,UndefinedElement
    if qname in ['http://example.com/newformat#','http://purl.org/atom/ns']:
      self.log(ObsoleteNamespace({"element":name, "namespace":qname}))
    elif name=='feed':
      self.log(InvalidNamespace({"element":name, "namespace":qname}))
    else:
      self.log(UndefinedElement({"parent":"root", "element":name}))

    from validators import any
    return any(self, name, qname, attrs)

  def do_rss(self):
    from rss import rss
    return rss()

  def do_feed(self):
    from logging import TYPE_PIE
    if self.getFeedType()==TYPE_PIE:
      from feed import pie_feed as feed
    else:
      from feed import feed
    return feed()

  def do_entry(self):
    from entry import entry
    return entry()

  def do_opml(self):
    from opml import opml
    return opml()

  def do_outlineDocument(self):
    from logging import ObsoleteVersion
    self.log(ObsoleteVersion({"element":"outlineDocument"}))

    from opml import opml
    return opml()

  def do_rdf_RDF(self):
    from rdf import rdf
    validatorBase.defaultNamespaces.append(purl1_namespace)
    return rdf()

  def do_Channel(self):
    from channel import rss10Channel
    return rss10Channel()

  def do_soap_Envelope(self):
    return root(self, self.xmlBase)

  def do_soap_Body(self):
    validatorBase.defaultNamespaces.append(soap_namespace)
    return root(self, self.xmlBase)

  def do_request(self):
    return root(self, self.xmlBase)

  def do_xhtml_html(self):
    from logging import UndefinedElement
    self.log(UndefinedElement({"parent":"root", "element":"xhtml:html"}))
    from validators import eater
    return eater()

__history__ = """
$Log$
Revision 1.17  2005/12/14 03:28:30  rubys
Use a more specific error

Revision 1.16  2005/12/14 03:15:53  rubys
"Possibly as early as October, and certainly no later than the end of the year, these warnings will be converted over to errors."

Revision 1.15  2005/11/08 18:27:42  rubys
Warn on missing language, itunes:explicit, or itunes:category if any itunes
elements are present.

Revision 1.14  2005/11/02 13:19:37  rubys
Apply patch 1345547

Revision 1.13  2005/10/30 21:34:50  rubys
Preliminary OMPL support

Revision 1.12  2005/09/15 17:04:13  rubys
Fix SOAP support (reported by: Martin Jansen)

Revision 1.11  2005/08/20 03:58:58  rubys
white-space + xml:base

Revision 1.10  2005/07/16 00:24:34  rubys
Through section 2

Revision 1.9  2005/07/15 11:17:24  rubys
Baby steps towards Atom 1.0 support

Revision 1.8  2005/01/28 00:06:25  josephw
Use separate 'item' and 'channel' classes to reject RSS 2.0 elements in
 RSS 1.0 feeds (closes 1037785).

Revision 1.7  2005/01/22 23:45:36  rubys
pass last rss11 test case (neg-ext-notrdf.xml)

Revision 1.6  2005/01/20 13:37:32  rubys
neg-anyarss test case from rss 1.1

Revision 1.5  2005/01/19 13:16:45  rubys
Recognize RSS11 as a member of the RSS1.0 family

Revision 1.4  2005/01/19 01:28:13  rubys
Initial support for rss 1.1

Revision 1.3  2005/01/14 01:23:28  josephw
Disallow 'channel' as a root element; closes 1000123.

Revision 1.2  2004/06/12 23:19:55  rubys
fix for bug 966458: Disallow namespace on the rss element

Revision 1.1.1.1  2004/02/03 17:33:16  rubys
Initial import.

Revision 1.18  2003/12/11 16:32:08  f8dy
fixed id tags in header

Revision 1.17  2003/08/23 21:01:00  rubys
Validate that content, content:encoded, and xhtml:body are safe

Revision 1.16  2003/08/05 07:59:04  rubys
Add feed(id,tagline,contributor)
Drop feed(subtitle), entry(subtitle)
Check for obsolete version, namespace
Check for incorrect namespace on feed element

Revision 1.15  2003/08/05 05:32:35  f8dy
0.2 snapshot - change version number and default namespace

Revision 1.14  2003/08/04 00:54:35  rubys
Log every valid element (for better self validation in test cases)

Revision 1.13  2003/07/09 16:24:30  f8dy
added global feed type support

Revision 1.12  2003/07/07 10:35:50  rubys
Complete first pass of echo/pie tests

Revision 1.11  2003/07/07 00:54:00  rubys
Rough in some pie/echo support

Revision 1.10  2002/12/22 23:56:09  rubys
Adjust names, add a WSDL

Revision 1.9  2002/10/18 13:06:57  f8dy
added licensing information

"""

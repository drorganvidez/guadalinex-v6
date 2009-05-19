<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

<!-- XSLT for db2mm
     db2mm XSLT converts a DocBook article to Moin markup
     CREATION INFO:
        Author: Jeff Schering
        Date: May 17, 2005
        Version: 0.1
     REVISION INFO:
        Author: Jeff Schering
        Date: June 5, 2005
        Version: 0.2
        Description: added rudimentary <table> and <informaltable> support, and
            <chapter> support for use with XInclude.
     REVISION INFO:
        Author: Jeff Schering
        Date: June 7, 2006
        Version: 0.3
        Description: changed license from CC-BY-SA to GPL
     REVISION INFO:
        Author: Mikko Virkkilä
        Date: July 7, 2006
        Version: 0.4
        Description: split in to multiple files, support for <section>, limitless 
        	depth for lists, glossdefs, better support for informaltable with attrs
	REVISION INFO:
        Author: Mikko Virkkilä
        Date: July 10, 2006
        Version: 0.5
        Description: renamed from a2m (previously known as art2moin) to db2mm, 
            improved variablelist, procedure an generic list handling 
            (varibablelist and procdeure handling was added in 0.4). 
        	Support for trademark-tag. Rudimentary image support.

	REVISION INFO:
        Author: Mikko Virkkilä
        Date: August 10, 2006
        Version: 0.6
        Description: Lots of small fixes, custom numbering methods for orderedlists,
            para is reworked to support block-elements.

        	
    Copyright 2005, 2006 by Jeff Schering (jeffschering@gmail.com)
	Copyright 2006 by Mikko Virkkila (mvirkkil@cc.hut.fi)

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program; if not, write to the Free Software
    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

  
-->

<xsl:output method="text" encoding="utf-8"/>
<!--<xsl:strip-space elements="article|chapter|colophon|appendix|glossary"/>-->
<xsl:strip-space elements="*" />

<xsl:include href="sections.xslt" />
<xsl:include href="tables.xslt" />
<xsl:include href="admonitions.xslt" />
<xsl:include href="lists.xslt" />
<xsl:include href="inlinestyles.xslt" />
<xsl:include href="graphics.xslt" />
<xsl:include href="para.xslt" />

<!--### Constants ###-->
<xsl:variable name="newline">
<xsl:text>
</xsl:text>
</xsl:variable>

<xsl:variable name="space">
  <xsl:text> </xsl:text>
</xsl:variable>

<!--### Parameters ###-->
<xsl:param name="root" select="/*" />

<!--### Main ###-->
<xsl:template match="/">
	<xsl:apply-templates select="$root"/>
	
	<xsl:if test="count(//footnote)>0">
		<xsl:text>[[FootNote()]]</xsl:text>
	</xsl:if>
</xsl:template>

<xsl:template match="article|chapter|colophon|appendix|glossary|bookinfo">
  <xsl:text>## Generator: a2m.xslt Version 0.6 </xsl:text>
  <xsl:value-of select="$newline"/>
  <xsl:apply-templates />
</xsl:template>

<!--pagename-->
<xsl:template match="article/title|chapter/title|colophon/title|appendix/title|glossary/title">
  <xsl:text>##Page is </xsl:text><xsl:value-of select="text()"/>
  <xsl:value-of select="$newline"/>
</xsl:template>



<xsl:template match="para/screen">
	<xsl:text>{{{</xsl:text>
	<xsl:value-of select="." />
	<xsl:text>}}}</xsl:text>
</xsl:template>

<xsl:template match="screen|programlisting|literallayout">
	<xsl:text>{{{</xsl:text>
	<xsl:value-of select="." />
	<xsl:text>}}}</xsl:text>
	<xsl:value-of select="$newline"/>
	<xsl:value-of select="$newline"/>
</xsl:template>



<xsl:template match="article/comment()">
  <xsl:value-of select="$newline"/>
  <xsl:text>## </xsl:text>
  <xsl:call-template name="inlinetext" />
  <xsl:value-of select="$newline"/>
</xsl:template>


<!-- Fallback, any logging should probably be done here -->
<xsl:template match="*">
<xsl:text>{{{&lt;</xsl:text><xsl:value-of select="local-name()"/><xsl:text>&gt;}}}</xsl:text>
<xsl:apply-templates />
<xsl:text>{{{&lt;/</xsl:text><xsl:value-of select="local-name()"/><xsl:text>&gt;}}}</xsl:text>
</xsl:template>

</xsl:stylesheet>





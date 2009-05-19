<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

<!-- XSLT for db2mm
    This file is part of db2mm, see db2mm.xslt for details

    Copyright 2005, 2006 by Jeff Schering (jeffschering@gmail.com)
	Copyright 2006 by Mikko Virkkilä (mvirkkil@cc.hut.fi)

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

<!--
### Admonitions ###
-->


<xsl:template match="note|tip|warning|caution|important">
 <xsl:text>[[Admonition("</xsl:text>
  <xsl:value-of select="local-name()"/><xsl:text>"</xsl:text>
  <xsl:apply-templates select="title"/>
  <xsl:apply-templates select="para"/>
  <xsl:text>)]]</xsl:text>
</xsl:template>

<xsl:template match="caution/title|important/title|note/title|tip/title|warning/title">
  <xsl:text>, title="</xsl:text>
  <xsl:value-of select="text()"/>
  <xsl:text>"</xsl:text>
</xsl:template>


<xsl:template match="caution/para|important/para|note/para|tip/para|warning/para">
  <xsl:text>, text="</xsl:text>
  <xsl:call-template name="inlinetext"/>
  <xsl:text>"</xsl:text>
</xsl:template>

</xsl:stylesheet>



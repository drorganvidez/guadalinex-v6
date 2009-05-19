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
### Sections ###
-->


<!-- section -->

<xsl:template match="section">
	<xsl:value-of select="$newline"/>
	<xsl:call-template name="heading"/>
	<xsl:text> </xsl:text><xsl:value-of select="./title"/><xsl:text> </xsl:text>
	<xsl:call-template name="heading"/>
	<xsl:value-of select="$newline"/>
    <xsl:apply-templates/>

</xsl:template>


<xsl:template name="heading">
	<xsl:for-each select="ancestor-or-self::section">
		<xsl:text>=</xsl:text>
	</xsl:for-each>
</xsl:template>

<!--
sect# 
-->

<xsl:template match="sect1">
  <xsl:value-of select="$newline"/>
  <xsl:text>== </xsl:text>
  <xsl:value-of select="title/text()"/>
  <xsl:text> ==</xsl:text>
  <xsl:value-of select="$newline"/>
  <xsl:apply-templates/>
</xsl:template>

<xsl:template match="sect2">
  <xsl:value-of select="$newline"/>
  <xsl:text>=== </xsl:text>
  <xsl:value-of select="title/text()"/>
  <xsl:text> ===</xsl:text>
  <xsl:value-of select="$newline"/>
  <xsl:apply-templates/>
</xsl:template>

<xsl:template match="sect3">
  <xsl:value-of select="$newline"/>
  <xsl:text>==== </xsl:text>
  <xsl:value-of select="title/text()"/>
  <xsl:text> ====</xsl:text>
  <xsl:value-of select="$newline"/>
  <xsl:apply-templates/>
</xsl:template>

<xsl:template match="sect4">
  <xsl:value-of select="$newline"/>
  <xsl:text>===== </xsl:text>
  <xsl:value-of select="title/text()"/>
  <xsl:text> =====</xsl:text>
  <xsl:value-of select="$newline"/>
  <xsl:apply-templates/>
</xsl:template>

<!--dummy, since already handled in sect-->
<xsl:template match="sect1/title|sect2/title|sect3/title|sect4/title|section/title">
</xsl:template>



</xsl:stylesheet>
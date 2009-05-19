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
### Table stuff ###
-->

<xsl:template match="informaltable|table">
  <xsl:value-of select="$newline"/>
  <xsl:apply-templates select="title"/>
  <xsl:apply-templates select="tgroup"/>
  <xsl:value-of select="$newline"/>
</xsl:template>

<xsl:template match="table/title">
	<xsl:text>||&lt;:-</xsl:text>
	<xsl:value-of select="../tgroup/@cols"/>
	<xsl:text>&gt;'''</xsl:text>
  	<xsl:value-of select="."/>
  	<xsl:text>'''||</xsl:text>
  	<xsl:value-of select="$newline"/>
</xsl:template>

<xsl:template match="tgroup">
  <xsl:apply-templates select="thead"/>
  <xsl:apply-templates select="tbody"/>
</xsl:template>

<xsl:template match="thead|tbody">
  <xsl:apply-templates select="row"/>
</xsl:template>


<xsl:template match="thead/row|tbody/row">
  <xsl:text>||</xsl:text>
  <xsl:apply-templates select="entry"/>
  <xsl:value-of select="$newline"/>
</xsl:template>

<xsl:template match="thead/row/entry">
  <!--<xsl:variable name="defaultattrs">:</xsl:variable>-->
  <xsl:call-template name="getentryattrs">
  	<xsl:with-param name="defaultattrs" select="':'"/>
  </xsl:call-template>
  <xsl:text>'''</xsl:text>
  <xsl:value-of select="."/>
  <xsl:text>'''||</xsl:text>
</xsl:template>



<xsl:template match="tbody/row/entry">
  <xsl:call-template name="getentryattrs"/>
  
  <xsl:variable name="var">
    <xsl:apply-templates/>
  </xsl:variable>
  <xsl:value-of select="normalize-space($var)"/>
  <!--<xsl:apply-templates select="para"/>-->
  <xsl:text>||</xsl:text>
</xsl:template>

<xsl:template match="tbody/row/entry/para">
  <xsl:variable name="var">
    <xsl:apply-templates />
  </xsl:variable>
  <xsl:value-of select="normalize-space($var)"/>
</xsl:template>



<!--
Returns a wiki styled syntax of a cell
<-3> means three columns wide
<|2> means two rows high
<|2-3> means two rows high and three columns wide
<)> - right aligned
<(> - left aligned
<:> - centered
<v> - bottom
<^> - top

To support colspan, the namest and nameend values need
to end with and underscore and the number of the column
like namest="col_3"
If the numbering starts at 0 or 1 makes no difference.
-->
<xsl:template name="getentryattrs">
  <xsl:param name="defaultattrs"/>

  <xsl:variable name="colw">
    <xsl:call-template name="getcolwidth"/>
  </xsl:variable>
  <xsl:variable name="rowh">
    <xsl:call-template name="getrowheight"/>
  </xsl:variable>
  <xsl:variable name="halign">
    <xsl:call-template name="gethorizontalalign"/>
  </xsl:variable>
  <xsl:variable name="valign">
    <xsl:call-template name="getverticalalign"/>
  </xsl:variable>
  
  
  <xsl:if test="$colw!='NaN' or $rowh!='NaN' or $halign!='' or $valign!='' or $defaultattrs!=''">
  	<xsl:text>&lt;</xsl:text>
  	<xsl:if test="$colw!='NaN'">
  		<xsl:text>-</xsl:text><xsl:value-of select="$colw"/>
  	</xsl:if>
  	
  	<xsl:if test="$rowh!='NaN'">
  		<xsl:text>|</xsl:text><xsl:value-of select="$rowh"/>
  	</xsl:if>
  	
  	<xsl:value-of select="$halign"/>
  	<xsl:value-of select="$valign"/>
  	<xsl:value-of select="$defaultattrs"/>
  	<xsl:text>></xsl:text>
  </xsl:if>
  
</xsl:template>


<xsl:template name="getcolwidth">
	<xsl:variable name="start">
		<xsl:value-of select="substring-after(@namest,'_')" />
	</xsl:variable>

	<xsl:variable name="end">
		<xsl:value-of select="substring-after(@nameend,'_')" />
	</xsl:variable>

	<xsl:value-of select="number($end) - number($start) + 1"/>
</xsl:template>

<xsl:template name="getrowheight">
	<xsl:value-of select="number(@morerows) + 1"/>
</xsl:template>


<xsl:template name="getverticalalign">
	<xsl:if test="@valign='top'">
		<xsl:text>^</xsl:text>
	</xsl:if>
	<xsl:if test="@valign='bottom'">
		<xsl:text>v</xsl:text>
	</xsl:if>
</xsl:template>

<xsl:template name="gethorizontalalign">
	<xsl:if test="@align='right'">
		<xsl:text>)</xsl:text>
	</xsl:if>
	<xsl:if test="@align='left'">
		<xsl:text>(</xsl:text>
	</xsl:if>
	<xsl:if test="@align='center'">
		<xsl:text>:</xsl:text>
	</xsl:if>
</xsl:template>


</xsl:stylesheet>



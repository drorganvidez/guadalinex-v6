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
### Lists ###
-->


<xsl:template match="variablelist">
	<xsl:apply-templates select="varlistentry"/>
	<xsl:value-of select="$newline" />
</xsl:template>

<xsl:template match="varlistentry">
	<xsl:apply-templates />
</xsl:template>

<xsl:template match="varlistentry/term">
	<xsl:call-template name="listdepth" /><xsl:text>. '''</xsl:text>
	<xsl:value-of select="text()"/>
	<xsl:text>'''</xsl:text>
	<xsl:value-of select="$newline" />
</xsl:template>

<xsl:template match="glosslist">
	<xsl:apply-templates />
	<xsl:value-of select="$newline"/>
</xsl:template>

<xsl:template match="glossterm">
	<xsl:value-of select="."/>
</xsl:template>


<xsl:template match="glosslist/glossentry">
	<xsl:text> </xsl:text>
	<xsl:apply-templates select="glossterm" /><xsl:text>::</xsl:text>
	
	<xsl:variable name="count">
		<xsl:value-of select="count(glossdef/para)" />
	</xsl:variable>
	
	<xsl:for-each select="glossdef/para">
		<xsl:if test="$count>1">
			<xsl:value-of select="$newline" />
			<xsl:text> ::</xsl:text>
		</xsl:if>

	    <xsl:text> </xsl:text>		
		<xsl:variable name="var">
		  	<xsl:apply-templates/>
	    </xsl:variable>
	    <xsl:value-of select="normalize-space($var)"/>

	</xsl:for-each>
	<xsl:value-of select="$newline" />
	<xsl:value-of select="$newline" />
	
</xsl:template>


<xsl:template match="orderedlist|itemizedlist|procedure|substeps">
  <xsl:apply-templates select="itemizedlist|orderedlist|listitem|procedure|step|substeps"/>
  
  <!-- extra newline if end of list, to make things pretty -->
  <!--<xsl:if test="count(ancestor::itemizedlist|ancestor::orderedlist|ancestor::procedure|ancestor::substeps)=0">
  	<xsl:value-of select="$newline" />
  </xsl:if>-->
</xsl:template>

<xsl:template name="listdepth">
	<xsl:for-each select="ancestor-or-self::listitem">
		<xsl:value-of select="$space" />
	</xsl:for-each>
	<xsl:for-each select="ancestor-or-self::step">
		<xsl:value-of select="$space" />
	</xsl:for-each>
	<xsl:for-each select="ancestor-or-self::varlistentry">
		<xsl:value-of select="$space" />
	</xsl:for-each>
</xsl:template>

<xsl:template name="listnumeration">
	<!-- gets first parent with the numeration attribute. Variable will be "" if none is found-->
	<xsl:variable name="numeration" select="ancestor::*[@numeration][1]/@numeration" />

	<xsl:choose>
		<!--
				'1': "arabic", (default)
				'a': "loweralpha", 
				'A': "upperalpha",
				'i': "lowerroman",
				'I': "upperroman"
		-->
		<xsl:when test="$numeration='loweralpha'">
			<xsl:text>a. </xsl:text>
		</xsl:when>
		<xsl:when test="$numeration='upperalpha'">
			<xsl:text>A. </xsl:text>
		</xsl:when>
		<xsl:when test="$numeration='lowerroman'">
			<xsl:text>i. </xsl:text>
		</xsl:when>
		<xsl:when test="$numeration='upperroman'">
			<xsl:text>I. </xsl:text>
		</xsl:when>
		<xsl:otherwise>
			<xsl:text>1. </xsl:text>
		</xsl:otherwise>
	</xsl:choose>
</xsl:template>


<xsl:template match="listitem/para|step/para">
  <xsl:if test="position()>1">
  	  <xsl:text>[[BR]][[BR]]</xsl:text>
  </xsl:if>
  
  <xsl:variable name="var">
	<xsl:apply-templates/>
  </xsl:variable>
  <xsl:value-of select="normalize-space($var)"/>

</xsl:template>



<xsl:template match="orderedlist/listitem|step">
	<xsl:call-template name="listdepth"/>
	<xsl:call-template name="listnumeration" />
	
	<xsl:variable name="var">
		<xsl:apply-templates select="para"/>
  	</xsl:variable>
  	<xsl:value-of select="normalize-space($var)"/>
	<xsl:value-of select="$newline"/>
	<xsl:apply-templates select="itemizedlist|varlistentry|orderedlist|step"/>
	
</xsl:template>


<xsl:template match="itemizedlist/listitem|varlistentry/listitem">
	<xsl:call-template name="listdepth"/><xsl:text>* </xsl:text>
	<xsl:variable name="var">
		<xsl:apply-templates select="para"/>
    </xsl:variable>
  	<xsl:value-of select="normalize-space($var)"/>
	<xsl:value-of select="$newline"/>
  	<xsl:apply-templates select="itemizedlist|varlistentry|orderedlist|step"/>

</xsl:template>


</xsl:stylesheet>

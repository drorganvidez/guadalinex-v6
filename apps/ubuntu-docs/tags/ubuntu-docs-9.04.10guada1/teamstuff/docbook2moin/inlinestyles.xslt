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
### Inline styles ###
-->


<xsl:template match="footnote">
	<xsl:text>[[FootNote("</xsl:text>
        <xsl:call-template name="inlinetext" />
	<xsl:text>")]]</xsl:text>
</xsl:template>

<xsl:template match="ulink">
  <xsl:text>[</xsl:text>
  <xsl:value-of select="@url" />
  <xsl:text> </xsl:text>
  <xsl:call-template name="inlinetext" />
  <xsl:text>]</xsl:text>
</xsl:template>

<xsl:template match="menuchoice|guibutton|guilabel|keycap|interface">
  <xsl:text>'''''</xsl:text>
  <xsl:apply-templates/>
  <xsl:text>'''''</xsl:text>
</xsl:template>

<xsl:template match="guisubmenu|guimenuitem">
  <xsl:text>&amp;rarr;</xsl:text>
  <xsl:value-of select="text()"/>
  <xsl:apply-templates select="guisubmenu|guimenuitem"/>
</xsl:template>



<xsl:template match="code|command|filename|application">
  <xsl:text>{{{</xsl:text>
  <xsl:call-template name="inlinetext"/>
  <xsl:text>}}}</xsl:text>
</xsl:template>

<xsl:template match="citetitle|quote|phrase">
  <xsl:text>''</xsl:text>
  <xsl:apply-templates />
  <xsl:text>''</xsl:text>
</xsl:template>

<xsl:template match="subscript">
  <xsl:text>,,</xsl:text>
  <xsl:apply-templates />
  <xsl:text>,,</xsl:text>
</xsl:template>

<xsl:template match="superscript">
  <xsl:text>^</xsl:text>
  <xsl:apply-templates />
  <xsl:text>^</xsl:text>
</xsl:template>


<!-- strikethrough -->
<xsl:template match="emphasis[@role='strikethrough']">
  <xsl:text>--(</xsl:text>
  <xsl:apply-templates />
  <xsl:text>)--</xsl:text>
</xsl:template>


<!-- underline -->
<xsl:template match="emphasis[@role='underline']">
  <xsl:text>__</xsl:text>
  <xsl:apply-templates />
  <xsl:text>__</xsl:text>
</xsl:template>

<!-- strong, bold -->
<xsl:template match="emphasis[@role='strong']|emphasis[@role='bold']">
  <xsl:text>'''</xsl:text>
  <xsl:apply-templates />
  <xsl:text>'''</xsl:text>
</xsl:template>

<!-- italic -->
<xsl:template match="emphasis|emphasis[@role='italic']">
  <xsl:text>''</xsl:text>
  <xsl:apply-templates />
  <xsl:text>''</xsl:text>
</xsl:template>



<xsl:template match="trademark">
  <xsl:apply-templates />
  <xsl:text>&amp;reg;</xsl:text>
</xsl:template>



<xsl:template name="inlinetext">
  <xsl:value-of select="normalize-space(.)" />
</xsl:template>




<!-- NO EFFECT! -->
<xsl:template match="guimenu|indexterm|firstterm">
  <xsl:value-of select="text()"/>
</xsl:template>

</xsl:stylesheet>

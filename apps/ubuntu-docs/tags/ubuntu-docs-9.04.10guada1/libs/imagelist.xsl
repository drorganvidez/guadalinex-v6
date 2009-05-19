<?xml version="1.0" encoding="UTF-8" ?>
<!--
   Author: Sean Wheller sean@inwords.co.za http://www.inwords.co.za
 -->
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
  <xsl:output method="text"/>
    <xsl:template match="book | article">
    <xsl:for-each select="//imagedata">
      <xsl:call-template name="script"/>
    </xsl:for-each>
 </xsl:template>
  <xsl:template name="script" match="imagedata">
    <xsl:value-of select="@fileref"/>
    <xsl:text> </xsl:text>
  </xsl:template>
</xsl:stylesheet>

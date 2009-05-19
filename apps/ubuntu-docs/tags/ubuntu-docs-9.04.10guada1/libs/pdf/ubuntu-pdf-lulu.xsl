<?xml version="1.0" encoding="ISO-8859-1"?>
<!-- Customization layer for PDF output 
     License: CC-BY-SA. see http://creativecommons.org/licenses/by-sa/2.0/
-->

<xsl:stylesheet version="1.0"
xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
xmlns:fo="http://www.w3.org/1999/XSL/Format">

<!-- Import our general pdf customisations -->
<xsl:import href="ubuntu-pdf.xsl"/>

<!-- ***************  Lulu tweaks  *********************  -->
<!-- ***************************************************  -->

<!-- Change the font, if you like, default is 11 -->
<xsl:param name="body.font.master">11</xsl:param>

<!-- Define the page width/height -->
<xsl:param name="page.width">18.9cm</xsl:param>
<xsl:param name="page.height">24.6cm</xsl:param>

<!-- It's a book, so this takes account for the binding  -->
<xsl:param name="double.sided" select="1"></xsl:param>

<!-- This causes some blank pages on the left hand side, so don't draw headers on those pages -->
<xsl:param name="headers.on.blank.pages" select="0"></xsl:param>

<!-- Split words across lines -->
<xsl:param name="hyphenate">true</xsl:param>

</xsl:stylesheet>


<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  version="1.0">
  
  <xsl:template name="header.navigation">
    <xsl:variable name="home" select="/*[1]"/>
    <xsl:variable name="up" select="parent::*"/>
      <div id="mastwrap">
      <div id="masthead">
        </div>
	</div>


      </xsl:template>

<xsl:template name="user.footer.navigation">
  <HR/>

<div id="footer">

  <div id="ubuntulinks">

	<xsl:apply-templates select="//copyright[1]" mode="titlepage.mode"/>
	<p><a href="https://launchpad.net/ubuntu-doc">Feedback</a></p>
	<p><a rel="license" href="http://creativecommons.org/licenses/by-sa/3.0/">
	<img alt="Creative Commons License" style="border-width:0" src="http://i.creativecommons.org/l/by-sa/3.0/80x15.png" />
	</a></p>

  </div>

</div>

</xsl:template>


<!-- ==================================================================== -->


</xsl:stylesheet>

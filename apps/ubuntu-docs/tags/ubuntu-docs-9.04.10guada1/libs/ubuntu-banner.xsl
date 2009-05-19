<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  version="1.0">

<!-- This adds the header -->

<xsl:template name="header.navigation">
	<div id="header">
	<div id="logo-floater"><h1><a href="http://help.ubuntu.com" title="Ubuntu Documentation"><img alt="Ubuntu" id="logo" src="https://help.ubuntu.com/htdocs/ubuntunew/img/logo.png" /></a></h1>
	</div>
	<div id="sitename"><a href="https://help.ubuntu.com/"><img alt="Official Documentation" src="http://doc.ubuntu.com/~mdke/help-about.png" /><span>Official Documentation</span></a></div>
	</div>
</xsl:template>

<!-- Breadcrumbs -->

<xsl:template name="breadcrumbs">
  <xsl:param name="this.node" select="."/>
  <div class="breadcrumbs">
	<a href="http://help.ubuntu.com/">Home</a>
      <xsl:text> &gt; </xsl:text>
    <xsl:for-each select="$this.node/ancestor::*">
      <span class="breadcrumb-link">
        <a>
          <xsl:attribute name="href">
            <xsl:call-template name="href.target">
              <xsl:with-param name="object" select="."/>
              <xsl:with-param name="context" select="$this.node"/>
            </xsl:call-template>
          </xsl:attribute>
          <xsl:apply-templates select="." mode="title.markup"/>
        </a>
      </span>
      <xsl:text> &gt; </xsl:text>
    </xsl:for-each>
    <!-- And display the current node, but not as a link -->
    <span class="breadcrumb-node">
      <xsl:apply-templates select="$this.node" mode="title.markup"/>
    </span>
  </div>
</xsl:template>

<!-- This adds the footer -->

<xsl:template name="user.footer.navigation">
<hr />
<div id="footer">

  <div id="ubuntulinks">

	<p>The material in this document is available under a free license, see <a href="legal.html">Legal</a> for details<br />
	For information on contributing or to report a problem, visit the <a href="https://bugs.launchpad.net/ubuntu-doc">Ubuntu Documentation Project</a></p>

  </div>

</div>

<div id="bottomcap">
	<img src="../../libs/img/cap-bottom.png" alt=""/>
</div>

</xsl:template>

<!-- This adds the wrapper elements -->

<xsl:template name="chunk-element-content">
  <xsl:param name="prev"/>
  <xsl:param name="next"/>
  <xsl:param name="nav.context"/>
  <xsl:param name="content">
    <xsl:apply-imports/>
  </xsl:param>

  <xsl:call-template name="user.preroot"/>

  <html>
    <xsl:call-template name="html.head">
      <xsl:with-param name="prev" select="$prev"/>
      <xsl:with-param name="next" select="$next"/>
    </xsl:call-template>

    <body>
	<div id="round">
	<img id="topcap" alt="" src="https://help.ubuntu.com/htdocs/ubuntunew/img/cap-top.png" />
	<div id="layout" class="container clear-block">
      <xsl:call-template name="body.attributes"/>
      <xsl:call-template name="user.header.navigation"/>

      <xsl:call-template name="header.navigation">
        <xsl:with-param name="prev" select="$prev"/>
        <xsl:with-param name="next" select="$next"/>
        <xsl:with-param name="nav.context" select="$nav.context"/>
      </xsl:call-template>

      <xsl:call-template name="user.header.content"/>
	<div id="page">
	<div id="content">
  	<xsl:call-template name="breadcrumbs"/>
      <xsl:copy-of select="$content"/>
	</div>
      <xsl:call-template name="user.footer.content"/>

      <xsl:call-template name="footer.navigation">
        <xsl:with-param name="prev" select="$prev"/>
        <xsl:with-param name="next" select="$next"/>
        <xsl:with-param name="nav.context" select="$nav.context"/>
      </xsl:call-template>

      <xsl:call-template name="user.footer.navigation"/>
	</div>
	</div>
	</div>
    </body>
  </html>
  <xsl:value-of select="$chunk.append"/>
</xsl:template>

</xsl:stylesheet>

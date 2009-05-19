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


<xsl:template match="para">
        <xsl:choose>
                <xsl:when test="count(table|informaltable|itemizedlist|orderedlist|simplelist|procedure|variablelist|blckquote)">
				<xsl:call-template name="handlepara">
                                <xsl:with-param name="curpos" select="1" />
                                <xsl:with-param name="pararoot" select="*|text()" />
                        </xsl:call-template>
                </xsl:when>
                <xsl:otherwise>
                        <xsl:variable name="txt">
                                <xsl:apply-templates/>
                        </xsl:variable>

                        <xsl:value-of select="normalize-space($txt)" />
                        <xsl:value-of select="$newline" />
                        <xsl:value-of select="$newline" />
                </xsl:otherwise>

        </xsl:choose>
</xsl:template>







<xsl:template name="handlepara">
        <xsl:param name="previouscontents" />
        <xsl:param name="curpos" />
        <xsl:param name="pararoot" />

        <xsl:variable name="curnode" select="node()[$curpos]" />
        <xsl:variable name="length" select="count($pararoot)"/>

        <xsl:choose>
                <xsl:when test="$curpos &gt; $length">
                        <xsl:variable name="contents">
                                <xsl:apply-templates select="$curnode" />
                        </xsl:variable>

                        <xsl:value-of select="normalize-space(concat($previouscontents,$contents))" />
                        <xsl:value-of select="$newline"/>
                        <xsl:value-of select="$newline"/>
                </xsl:when>

                <xsl:when test=    "local-name($curnode) = 'table' or
                                    local-name($curnode) = 'informaltable' or
                                    local-name($curnode) = 'glosslist' or
                                    local-name($curnode) = 'itemizedlist' or
                                    local-name($curnode) = 'orderedlist' or
                                    local-name($curnode) = 'simplelist' or
                                    local-name($curnode) = 'variablelist' or
                                    local-name($curnode) = 'literallayout' or
                                    local-name($curnode) = 'programlisting' or
                                    local-name($curnode) = 'blockquote'">


                        <xsl:value-of select="normalize-space($previouscontents)" />
                        <xsl:value-of select="$newline"/>
                        <xsl:apply-templates select="$curnode"/>
                        <xsl:value-of select="$newline"/>
                        <xsl:call-template name="handlepara">
                                <xsl:with-param name="curpos" select="$curpos+1"/>
                                <xsl:with-param name="pararoot" select="$pararoot"/>
                        </xsl:call-template>
                </xsl:when>

                <xsl:otherwise>
                        <xsl:variable name="contents">
                                <xsl:apply-templates select="$curnode" />
                        </xsl:variable>

                        <xsl:call-template name="handlepara">
                                <xsl:with-param name="previouscontents" select="concat($previouscontents, $contents)"/>
                                <xsl:with-param name="curpos" select="$curpos+1"/>
                                <xsl:with-param name="pararoot" select="$pararoot"/>
                        </xsl:call-template>
                </xsl:otherwise>
        </xsl:choose>

</xsl:template>

</xsl:stylesheet>

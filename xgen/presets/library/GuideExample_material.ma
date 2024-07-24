//Maya ASCII 2017ff03 scene
//Name: GuideEx_material.ma
//Last modified: Tue, May 03, 2016 03:50:22 PM
//Codeset: 1252
requires maya "2017ff03";
requires -nodeType "hairPhysicalShader" "hairPhysicalShader" "1.0";
requires -dataType "xgmGuideData" -dataType "igmDescriptionData" -dataType "xgmSplineData"
		 -dataType "xgmMeshData" -dataType "xgmSplineTweakData" -dataType "xgmSplineBoundInfoData"
		 -dataType "xgmGuideRefData" "xgenToolkit" "1.0";
requires "stereoCamera" "10.0";
requires "stereoCamera" "10.0";
currentUnit -l centimeter -a degree -t film;
fileInfo "application" "maya";
fileInfo "product" "Maya 2017";
fileInfo "version" "Preview Release 66";
fileInfo "cutIdentifier" "201605030300-993805-2";
fileInfo "osv" "Microsoft Windows 7 Business Edition, 64-bit Windows 7 Service Pack 1 (Build 7601)\n";
createNode shadingEngine -n "hairPhysicalShader7SG";
	rename -uid "98C28ED1-44B1-7467-3536-A79BA1F3E987";
	setAttr ".ihi" 0;
	setAttr -s 47 ".dsm";
	setAttr ".ro" yes;
createNode materialInfo -n "materialInfo47";
	rename -uid "6307EBE5-4F2D-9AC8-5508-44A2D0C3AE73";
createNode hairPhysicalShader -n "GuidehairPhysicalShader";
	rename -uid "3BA28E23-446F-3E4C-3E9C-ED9E9E31021B";
	setAttr ".rcD" -type "float3" 0.075907588 0.050605047 0.025302524 ;
	setAttr ".tcD" -type "float3" 0.61716169 0.41144103 0.20572051 ;
	setAttr ".ai_kd_ind" 0.80000001192092896;
createNode lightLinker -s -n "lightLinker1";
	rename -uid "647AD112-4AEA-1E39-1365-158E7393B12F";
	setAttr -s 38 ".lnk";
	setAttr -s 38 ".slnk";
select -ne :time1;
	setAttr -av -k on ".cch";
	setAttr -cb on ".ihi";
	setAttr -av -k on ".nds";
	setAttr -cb on ".bnm";
	setAttr ".o" 1;
	setAttr -av ".unw" 1;
select -ne :hardwareRenderingGlobals;
	setAttr ".otfna" -type "stringArray" 22 "NURBS Curves" "NURBS Surfaces" "Polygons" "Subdiv Surface" "Particles" "Particle Instance" "Fluids" "Strokes" "Image Planes" "UI" "Lights" "Cameras" "Locators" "Joints" "IK Handles" "Deformers" "Motion Trails" "Components" "Hair Systems" "Follicles" "Misc. UI" "Ornaments"  ;
	setAttr ".otfva" -type "Int32Array" 22 0 1 1 1 1 1
		 1 1 1 0 0 0 0 0 0 0 0 0
		 0 0 0 0 ;
	setAttr ".mhl" 16;
	setAttr ".hwi" yes;
	setAttr ".ta" 3;
	setAttr ".aoon" yes;
	setAttr ".aosm" 32;
	setAttr -k on ".mbsof";
	setAttr ".aasc" 16;
	setAttr ".laa" yes;
	setAttr ".fprt" yes;
select -ne :renderPartition;
	setAttr -k on ".cch";
	setAttr -cb on ".ihi";
	setAttr -k on ".nds";
	setAttr -cb on ".bnm";
	setAttr -s 22 ".st";
	setAttr -cb on ".an";
	setAttr -cb on ".pt";
select -ne :renderGlobalsList1;
	setAttr -k on ".cch";
	setAttr -cb on ".ihi";
	setAttr -k on ".nds";
	setAttr -cb on ".bnm";
select -ne :defaultShaderList1;
	setAttr -k on ".cch";
	setAttr -cb on ".ihi";
	setAttr -k on ".nds";
	setAttr -cb on ".bnm";
	setAttr -s 25 ".s";
select -ne :postProcessList1;
	setAttr -k on ".cch";
	setAttr -cb on ".ihi";
	setAttr -k on ".nds";
	setAttr -cb on ".bnm";
	setAttr -s 2 ".p";
select -ne :defaultRenderingList1;
select -ne :lightList1;
	setAttr -s 3 ".l";
select -ne :lambert1;
	setAttr ".c" -type "float3" 0.044 0.020983513 0.0099879997 ;
select -ne :initialShadingGroup;
	setAttr -k on ".cch";
	setAttr -cb on ".ihi";
	setAttr -av -k on ".nds";
	setAttr -cb on ".bnm";
	setAttr -k on ".mwc";
	setAttr -cb on ".an";
	setAttr -cb on ".il";
	setAttr -cb on ".vo";
	setAttr -cb on ".eo";
	setAttr -cb on ".fo";
	setAttr -cb on ".epo";
	setAttr ".ro" yes;
select -ne :initialParticleSE;
	setAttr -av -k on ".cch";
	setAttr -cb on ".ihi";
	setAttr -av -k on ".nds";
	setAttr -cb on ".bnm";
	setAttr -k on ".mwc";
	setAttr -cb on ".an";
	setAttr -cb on ".il";
	setAttr -cb on ".vo";
	setAttr -cb on ".eo";
	setAttr -cb on ".fo";
	setAttr -cb on ".epo";
	setAttr ".ro" yes;
select -ne :defaultRenderGlobals;
	setAttr -k on ".cch";
	setAttr -k on ".ihi";
	setAttr -k on ".nds";
	setAttr -k on ".bnm";
	setAttr -k on ".macc";
	setAttr -k on ".macd";
	setAttr -k on ".macq";
	setAttr -k on ".mcfr";
	setAttr -k on ".ifg";
	setAttr -k on ".clip";
	setAttr -k on ".edm";
	setAttr -k on ".edl";
	setAttr ".ren" -type "string" "arnold";
	setAttr -av -k on ".esr";
	setAttr -k on ".ors";
	setAttr -k on ".sdf";
	setAttr -av ".outf" 51;
	setAttr -cb on ".imfkey" -type "string" "exr";
	setAttr -k on ".gama";
	setAttr -k on ".an";
	setAttr -k on ".ar";
	setAttr -k on ".fs";
	setAttr -k on ".ef";
	setAttr -av -k on ".bfs";
	setAttr -k on ".me";
	setAttr -k on ".se";
	setAttr -k on ".be";
	setAttr -k on ".ep";
	setAttr -k on ".fec";
	setAttr -av -k on ".ofc";
	setAttr -k on ".ofe";
	setAttr -k on ".efe";
	setAttr -k on ".oft";
	setAttr -k on ".umfn";
	setAttr -k on ".ufe";
	setAttr -k on ".pff";
	setAttr -k on ".peie";
	setAttr -k on ".ifp";
	setAttr -k on ".comp";
	setAttr -k on ".cth";
	setAttr -k on ".soll";
	setAttr -k on ".rd";
	setAttr -k on ".lp";
	setAttr -av -k on ".sp";
	setAttr -k on ".shs";
	setAttr -av -k on ".lpr";
	setAttr -k on ".gv";
	setAttr -k on ".sv";
	setAttr -k on ".mm";
	setAttr -k on ".npu";
	setAttr -k on ".itf";
	setAttr -k on ".shp";
	setAttr -k on ".isp";
	setAttr -k on ".uf";
	setAttr -k on ".oi";
	setAttr -k on ".rut";
	setAttr -k on ".mb";
	setAttr -av -k on ".mbf";
	setAttr -k on ".afp";
	setAttr -k on ".pfb";
	setAttr ".pram" -type "string" "XgPreRendering;";
	setAttr -k on ".poam";
	setAttr -k on ".prlm";
	setAttr -k on ".polm";
	setAttr -k on ".prm";
	setAttr ".pom" -type "string" "xgmCache -clearPtexCache;";
	setAttr -k on ".pfrm";
	setAttr -k on ".pfom";
	setAttr -av -k on ".bll";
	setAttr -k on ".bls";
	setAttr -av -k on ".smv";
	setAttr -k on ".ubc";
	setAttr -k on ".mbc";
	setAttr -k on ".mbt";
	setAttr -k on ".udbx";
	setAttr -k on ".smc";
	setAttr -k on ".kmv";
	setAttr -k on ".isl";
	setAttr -k on ".ism";
	setAttr -k on ".imb";
	setAttr -k on ".rlen";
	setAttr -av -k on ".frts";
	setAttr -k on ".tlwd";
	setAttr -k on ".tlht";
	setAttr -k on ".jfc";
	setAttr -k on ".rsb";
	setAttr -k on ".ope";
	setAttr -k on ".oppf";
	setAttr -k on ".hbl";
select -ne :defaultResolution;
	setAttr -av -k on ".cch";
	setAttr -k on ".ihi";
	setAttr -av -k on ".nds";
	setAttr -k on ".bnm";
	setAttr -av ".w" 1920;
	setAttr -av ".h" 1080;
	setAttr -av ".pa" 1;
	setAttr -av -k on ".al";
	setAttr -av ".dar" 1.7769999504089355;
	setAttr -av -k on ".ldar";
	setAttr -k on ".dpi";
	setAttr -av -k on ".off";
	setAttr -av -k on ".fld";
	setAttr -av -k on ".zsl";
	setAttr -k on ".isu";
	setAttr -k on ".pdu";
select -ne :defaultLightSet;
	setAttr -s 3 ".dsm";
select -ne :hardwareRenderGlobals;
	setAttr -k on ".cch";
	setAttr -cb on ".ihi";
	setAttr -k on ".nds";
	setAttr -cb on ".bnm";
	setAttr ".ctrs" 256;
	setAttr -av ".btrs" 512;
	setAttr -k off ".fbfm";
	setAttr -k off -cb on ".ehql";
	setAttr -k off -cb on ".eams";
	setAttr -k off -cb on ".eeaa";
	setAttr -k off -cb on ".engm";
	setAttr -k off -cb on ".mes";
	setAttr -k off -cb on ".emb";
	setAttr -av -k off -cb on ".mbbf";
	setAttr -k off -cb on ".mbs";
	setAttr -k off -cb on ".trm";
	setAttr -k off -cb on ".tshc";
	setAttr -k off ".enpt";
	setAttr -k off -cb on ".clmt";
	setAttr -k off -cb on ".tcov";
	setAttr -k off -cb on ".lith";
	setAttr -k off -cb on ".sobc";
	setAttr -k off -cb on ".cuth";
	setAttr -k off -cb on ".hgcd";
	setAttr -k off -cb on ".hgci";
	setAttr -k off -cb on ".mgcs";
	setAttr -k off -cb on ".twa";
	setAttr -k off -cb on ".twz";
	setAttr -k on ".hwcc";
	setAttr -k on ".hwdp";
	setAttr -k on ".hwql";
	setAttr -k on ".hwfr";
connectAttr "GuidehairPhysicalShader.oc" "hairPhysicalShader7SG.ss";
connectAttr "xgGuide90Shape.iog" "hairPhysicalShader7SG.dsm" -na;
connectAttr "xgGuide89Shape.iog" "hairPhysicalShader7SG.dsm" -na;
connectAttr "xgGuide88Shape.iog" "hairPhysicalShader7SG.dsm" -na;
connectAttr "xgGuide87Shape.iog" "hairPhysicalShader7SG.dsm" -na;
connectAttr "xgGuide86Shape.iog" "hairPhysicalShader7SG.dsm" -na;
connectAttr "xgGuide85Shape.iog" "hairPhysicalShader7SG.dsm" -na;
connectAttr "xgGuide84Shape.iog" "hairPhysicalShader7SG.dsm" -na;
connectAttr "xgGuide83Shape.iog" "hairPhysicalShader7SG.dsm" -na;
connectAttr "xgGuide82Shape.iog" "hairPhysicalShader7SG.dsm" -na;
connectAttr "xgGuide81Shape.iog" "hairPhysicalShader7SG.dsm" -na;
connectAttr "xgGuide80Shape.iog" "hairPhysicalShader7SG.dsm" -na;
connectAttr "xgGuide79Shape.iog" "hairPhysicalShader7SG.dsm" -na;
connectAttr "xgGuide78Shape.iog" "hairPhysicalShader7SG.dsm" -na;
connectAttr "xgGuide77Shape.iog" "hairPhysicalShader7SG.dsm" -na;
connectAttr "xgGuide76Shape.iog" "hairPhysicalShader7SG.dsm" -na;
connectAttr "xgGuide75Shape.iog" "hairPhysicalShader7SG.dsm" -na;
connectAttr "xgGuide74Shape.iog" "hairPhysicalShader7SG.dsm" -na;
connectAttr "xgGuide73Shape.iog" "hairPhysicalShader7SG.dsm" -na;
connectAttr "xgGuide72Shape.iog" "hairPhysicalShader7SG.dsm" -na;
connectAttr "xgGuide71Shape.iog" "hairPhysicalShader7SG.dsm" -na;
connectAttr "xgGuide70Shape.iog" "hairPhysicalShader7SG.dsm" -na;
connectAttr "xgGuide69Shape.iog" "hairPhysicalShader7SG.dsm" -na;
connectAttr "xgGuide68Shape.iog" "hairPhysicalShader7SG.dsm" -na;
connectAttr "xgGuide67Shape.iog" "hairPhysicalShader7SG.dsm" -na;
connectAttr "xgGuide66Shape.iog" "hairPhysicalShader7SG.dsm" -na;
connectAttr "xgGuide65Shape.iog" "hairPhysicalShader7SG.dsm" -na;
connectAttr "xgGuide64Shape.iog" "hairPhysicalShader7SG.dsm" -na;
connectAttr "xgGuide63Shape.iog" "hairPhysicalShader7SG.dsm" -na;
connectAttr "xgGuide62Shape.iog" "hairPhysicalShader7SG.dsm" -na;
connectAttr "xgGuide61Shape.iog" "hairPhysicalShader7SG.dsm" -na;
connectAttr "xgGuide60Shape.iog" "hairPhysicalShader7SG.dsm" -na;
connectAttr "xgGuide59Shape.iog" "hairPhysicalShader7SG.dsm" -na;
connectAttr "xgGuide58Shape.iog" "hairPhysicalShader7SG.dsm" -na;
connectAttr "xgGuide57Shape.iog" "hairPhysicalShader7SG.dsm" -na;
connectAttr "xgGuide56Shape.iog" "hairPhysicalShader7SG.dsm" -na;
connectAttr "xgGuide55Shape.iog" "hairPhysicalShader7SG.dsm" -na;
connectAttr "xgGuide54Shape.iog" "hairPhysicalShader7SG.dsm" -na;
connectAttr "xgGuide53Shape.iog" "hairPhysicalShader7SG.dsm" -na;
connectAttr "xgGuide52Shape.iog" "hairPhysicalShader7SG.dsm" -na;
connectAttr "xgGuide51Shape.iog" "hairPhysicalShader7SG.dsm" -na;
connectAttr "xgGuide50Shape.iog" "hairPhysicalShader7SG.dsm" -na;
connectAttr "xgGuide49Shape.iog" "hairPhysicalShader7SG.dsm" -na;
connectAttr "xgGuide48Shape.iog" "hairPhysicalShader7SG.dsm" -na;
connectAttr "xgGuide47Shape.iog" "hairPhysicalShader7SG.dsm" -na;
connectAttr "xgGuide46Shape.iog" "hairPhysicalShader7SG.dsm" -na;
connectAttr "pSphere1_GuideExShape.iog" "hairPhysicalShader7SG.dsm" -na;
connectAttr "GuideExShape.iog" "hairPhysicalShader7SG.dsm" -na;
connectAttr "hairPhysicalShader7SG.msg" "materialInfo47.sg";
connectAttr "GuidehairPhysicalShader.msg" "materialInfo47.m";
connectAttr "GuidehairPhysicalShader.msg" "materialInfo47.t" -na;
relationship "link" ":lightLinker1" ":initialShadingGroup.message" ":defaultLightSet.message";
relationship "link" ":lightLinker1" ":initialParticleSE.message" ":defaultLightSet.message";
relationship "link" ":lightLinker1" "hairPhysicalShader7SG.message" ":defaultLightSet.message";
relationship "shadowLink" ":lightLinker1" ":initialShadingGroup.message" ":defaultLightSet.message";
relationship "shadowLink" ":lightLinker1" ":initialParticleSE.message" ":defaultLightSet.message";
relationship "shadowLink" ":lightLinker1" "hairPhysicalShader7SG.message" ":defaultLightSet.message";
connectAttr "hairPhysicalShader7SG.pa" ":renderPartition.st" -na;
connectAttr "GuidehairPhysicalShader.msg" ":defaultShaderList1.s" -na;
// End of GuideEx_material.ma
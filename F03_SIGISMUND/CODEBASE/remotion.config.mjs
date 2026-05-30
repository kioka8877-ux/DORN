import { Config } from "@remotion/cli/config";

// Rendu logiciel — pas de GPU requis (Colab / Modal)
Config.setChromiumOpenGlRenderer("swangle");
Config.setOverwriteOutput(true);
Config.setVideoImageFormat("jpeg");
Config.setJpegQuality(95);
Config.setConcurrency(1);

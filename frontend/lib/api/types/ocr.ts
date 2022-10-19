/* tslint:disable */
/* eslint-disable */
/**
/* This file was automatically generated from pydantic models by running pydantic2ts.
/* Do not modify it by hand - just update the pydantic models and then re-run the script
*/

export interface OcrAssetReq {
  recipeSlug: string;
  assetName: string;
}
export interface OcrTsvResponse {
  level?: number;
  pageNum?: number;
  blockNum?: number;
  parNum?: number;
  lineNum?: number;
  wordNum?: number;
  left?: number;
  top?: number;
  width?: number;
  height?: number;
  conf?: number;
  text?: string;
}

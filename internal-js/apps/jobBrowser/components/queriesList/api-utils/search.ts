/**
 * Licensed to Cloudera, Inc. under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  Cloudera, Inc. licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License.  You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

import axios, { AxiosResponse } from 'axios';
import { Facet, FieldInfo, Query, Search, SearchMeta } from '../index';
// Uncomment to serve mock response instead of calling the API endpoints
// import '../test/mockSearchHelper';

const SEARCH_URL = '/jobbrowser/query-proxy/api/query/search';

export interface SearchFacet {
  field: string;
  values: string[];
}

export interface SearchRequest {
  endTime: number;
  limit: number;
  offset: number;
  text?: string;
  facets?: SearchFacet[];
  sortText: string;
  startTime: number;
}

export interface SearchResponse {
  meta: SearchMeta;
  queries: Query[];
}

export const searchQueries = async (options: SearchRequest): Promise<SearchResponse> => {
  const response = await axios.post<SearchRequest, AxiosResponse<SearchResponse>>(SEARCH_URL, {
    search: { ...options, type: 'BASIC' }
  });
  return response.data;
};

// eslint-disable-next-line @typescript-eslint/no-unused-vars
export const deleteSearch = async (search: Search): Promise<void> => {
  // TODO: Implement POST ...
};

// eslint-disable-next-line @typescript-eslint/no-unused-vars
export const saveSearch = async (options: {
  name: string;
  category: string;
  type: string;
  entity: string;
  clause: string;
}): Promise<void> => {
  // TODO: Implement POST ...
};

// eslint-disable-next-line @typescript-eslint/no-unused-vars
export const fetchSuggestedSearches = async (options: {
  entityType: string;
}): Promise<Search[]> => {
  // TODO: Implement GET 'api/suggested-searches?entityType=x'
  const response = { searches: [] };
  return response.searches;
};

// eslint-disable-next-line @typescript-eslint/no-unused-vars
export const fetchFacets = async (options: {
  startTime: number;
  endTime: number;
  facetFields: string;
}): Promise<{ facets: Facet[]; rangeFacets: unknown[] }> => {
  // TODO: Implement GET '/api/query/facets?startTime=x&endTime=y&facetFields=z'
  return { facets: [], rangeFacets: [] };
};

export const fetchFieldsInfo = async (): Promise<FieldInfo[]> => {
  // TODO: Implement GET '/api/query/fields-information'
  const response = { fieldsInfo: [] };
  return response.fieldsInfo;
};

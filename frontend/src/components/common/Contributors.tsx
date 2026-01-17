/**
 * Copyright 2024-2026 Cerebro-Red v2 Contributors
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

/**
 * Contributors component displaying project contributors.
 */

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

interface Contributor {
  name: string;
  displayName?: string;
  avatar?: string;
}

const contributors: Contributor[] = [
  {
    name: 'Leviticus-Triage',
    displayName: 'Leviticus-Triage',
  },
];

export function Contributors() {
  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>Contributors</CardTitle>
          <Badge variant="secondary">{contributors.length}</Badge>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {contributors.map((contributor) => (
            <div key={contributor.name} className="flex items-center gap-3">
              <div className="h-10 w-10 rounded-full bg-primary/10 flex items-center justify-center">
                {contributor.avatar ? (
                  <img
                    src={contributor.avatar}
                    alt={contributor.name}
                    className="h-10 w-10 rounded-full"
                  />
                ) : (
                  <span className="text-primary font-semibold">
                    {contributor.name.charAt(0).toUpperCase()}
                  </span>
                )}
              </div>
              <div className="flex-1">
                <div className="font-medium">{contributor.name}</div>
                {contributor.displayName && contributor.displayName !== contributor.name && (
                  <div className="text-sm text-muted-foreground">{contributor.displayName}</div>
                )}
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}

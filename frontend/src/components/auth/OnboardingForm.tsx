'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { GitTemplate, ResourceClass } from '@/types/workspace';
import { CreateWorkspaceForm } from '@/components/workspace/CreateWorkspaceForm';

interface OnboardingFormProps {
  templates: GitTemplate[];
  resources: ResourceClass[];
}

export function OnboardingForm({ templates, resources }: OnboardingFormProps) {
  const router = useRouter();
  const [step, setStep] = useState(1);

  const handleWorkspaceCreated = () => {
    router.push('/dashboard');
  };

  return (
    <div className="max-w-4xl mx-auto py-10 px-4">
      <div className="space-y-6">
        <div className="text-center">
          <h1 className="text-3xl font-bold">Welcome to Your Development Environment</h1>
          <p className="text-muted-foreground mt-2">Let's get you set up with your first workspace</p>
        </div>

        <div className="flex justify-center space-x-2 mb-8">
          {[1, 2].map((i) => (
            <div
              key={i}
              className={`w-3 h-3 rounded-full ${
                step >= i ? 'bg-primary' : 'bg-muted'
              }`}
            />
          ))}
        </div>

        {step === 1 ? (
          <Card>
            <CardHeader>
              <CardTitle>Choose Your Path</CardTitle>
              <CardDescription>
                Select how you want to start your development journey
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <Button
                variant="outline"
                className="w-full justify-start h-auto p-4"
                onClick={() => setStep(2)}
              >
                <div className="text-left">
                  <div className="font-semibold">Start with a Template</div>
                  <div className="text-sm text-muted-foreground">
                    Choose from our pre-configured development environments
                  </div>
                </div>
              </Button>
            </CardContent>
          </Card>
        ) : (
          <CreateWorkspaceForm
            templates={templates}
            resources={resources}
            onSuccess={handleWorkspaceCreated}
          />
        )}

        {step > 1 && (
          <Button
            variant="ghost"
            onClick={() => setStep(step - 1)}
            className="mt-4"
          >
            Back
          </Button>
        )}
      </div>
    </div>
  );
}

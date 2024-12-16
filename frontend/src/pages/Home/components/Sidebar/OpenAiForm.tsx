import { zodResolver } from '@hookform/resolvers/zod';
import { useEffect, useState } from 'react';
import { useForm } from 'react-hook-form';
import { z } from 'zod';

import { FormGroup } from '@/components/FormGroup';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Label } from '@/components/ui/Label';
import { storageKeys } from '@/config/storageKeys';

import { useChat } from '../../contexts/ChatContext';

const openAiFormSchema = z.object({
  key: z.string().min(1, { message: 'Key is required.' }),
});

type OpenAiFormData = z.infer<typeof openAiFormSchema>;

export function OpenAiForm() {
  const [isEditable, setIsEditable] = useState(true);

  const { handleOpenAiKey } = useChat();

  const {
    formState: { isSubmitting, errors },
    register,
    handleSubmit,
    setValue,
  } = useForm<OpenAiFormData>({
    resolver: zodResolver(openAiFormSchema),
  });

  function handleEditable() {
    setValue('key', '');
    setIsEditable(true);
  }

  function onSubmit({ key }: OpenAiFormData) {
    handleOpenAiKey(key);
    localStorage.setItem(storageKeys.openAiKey, key);
    setIsEditable(false);
    setValue('key', '************');
  }

  useEffect(() => {
    const storage = localStorage.getItem(storageKeys.openAiKey);

    if (storage) {
      handleOpenAiKey(storage);
      setIsEditable(false);
      setValue('key', '************');
    }
  }, [handleOpenAiKey, setValue]);

  return (
    <form className="space-y-2" onSubmit={handleSubmit(onSubmit)}>
      <FormGroup
        className="space-y-2"
        error={{
          message: errors.key?.message,
          font: 'xs',
          align: 'left',
        }}
      >
        <Label htmlFor="openapi">Enter your Open AI Key</Label>
        <Input id="openapi" disabled={!isEditable} {...register('key')} />
      </FormGroup>

      {isEditable && (
        <Button type="submit" disabled={isSubmitting} className="w-full">
          Save
        </Button>
      )}

      {!isEditable && (
        <Button type="button" className="w-full" onClick={handleEditable}>
          Edit
        </Button>
      )}
    </form>
  );
}

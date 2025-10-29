import { cn } from '../client/cn';
import { useState, useEffect, FormEvent } from 'react';
import type { File } from 'wasp/entities';
import { useQuery, getAllFilesByUser } from 'wasp/client/operations';

export default function DbQueryPage() {

  const allUserFiles = useQuery(getAllFilesByUser, undefined, {
    // We disable automatic refetching because otherwise files would be refetched after `createFile` is called and the S3 URL is returned, 
    // which happens before the file is actually fully uploaded. Instead, we manually (re)fetch on mount and after the upload is complete.
    enabled: false,
  });

  useEffect(() => {
    allUserFiles.refetch();
  }, []);

  return (
    <div className='py-10 lg:mt-10'>
      <div className='mx-auto max-w-7xl px-6 lg:px-8'>
        <div className='mx-auto max-w-4xl text-center'>
          <h2 className='mt-2 text-4xl font-bold tracking-tight text-gray-900 sm:text-5xl dark:text-white'>
            <span className='text-yellow-500'>AWS</span> File Upload
          </h2>
        </div>
        <p className='mx-auto mt-6 max-w-2xl text-center text-lg leading-8 text-gray-600 dark:text-white'>
          This is an example file upload page using AWS S3. Maybe your app needs this. Maybe it doesn't. But a
          lot of people asked for this feature, so here you go 🤝
        </p>
        <div className='my-8 border rounded-3xl border-gray-900/10 dark:border-gray-100/10'>
          <div className='space-y-10 my-10 py-8 px-4 mx-auto sm:max-w-lg'>

            <div className='border-b-2 border-gray-200 dark:border-gray-100/10'></div>
            <div className='space-y-4 col-span-full'>
              <h2 className='text-xl font-bold'>Uploaded Files</h2>
              {allUserFiles.isLoading && <p>Loading...</p>}
              {allUserFiles.error && <p>Error: {allUserFiles.error.message}</p>}
              {!!allUserFiles.data && allUserFiles.data.length > 0 && !allUserFiles.isLoading ? (
                allUserFiles.data.map((file: File) => (
                  <div
                    key={file.key}
                    className={cn(
                      'flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3'
                    )}
                  >
                    <p>{file.name}</p>
                  </div>
                ))
              ) : (
                <p>No files uploaded yet :(</p>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}